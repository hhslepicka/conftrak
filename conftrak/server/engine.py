import tornado.web
from tornado import gen
import pymongo
import jsonschema
import ujson
from conftrak.server import utils
from jsonschema.exceptions import ValidationError, SchemaError
from pymongo.errors import PyMongoError


def db_connect(database, mongo_host, mongo_port):
    """Helper function to deal with stateful connections to MongoDB
    Connection established lazily. Connects to the database on request.
    Same connection pool is used for all clients per recommended by
    tornado developer manual.
    Parameters
    ----------
    database: str
        The name of database pymongo creates and/or connects
    host: str
        Name/address of the server that mongo daemon lives
    port: int
        Port num of the server
    Returns pymongo.database.Database
    -------
        Async server object which comes in handy as server has to juggle
    multiple clients and makes no difference for a single client compared
    to pymongo
    """
    try:
        client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
    except pymongo.errors.ConnectionFailure:
        raise utils.ConfTrakException("Unable to connect to MongoDB server...")
    database = client[database]
    return database


class DefaultHandler(tornado.web.RequestHandler):
    """DefaultHandler which takes care of CORS. Javascript needs this.
    In general, methods on RequestHandler and elsewhere in Tornado
    are not thread-safe. In particular, methods such as write(),
    finish(), and flush() must only be called from the main thread.
    If you use multiple threads it is important to use IOLoop.add_callback
    to transfer control back to the main thread before finishing the request.
    """
    @tornado.web.asynchronous
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def data_received(self, chunk):
        """Abstract method, overwrite potential default"""
        pass


class ConfigurationReferenceHandler(DefaultHandler):
    """Handler for ConfigurationReference insert, update, and querying.
    A RESTful handler, nothing fancy or stateful about this
    Methods
    --------
    get()
        Query 'configuration_referenece' documents given certain parameters.
    Pass 'num' in order to obtain the last 'num' configuration references.
    post()
        Insert 'configuration' documents
    put()
        Update or Insert if 'configuration' document does not exist.
    Update supports both field update and document replacement. If you
    would like to replace a document, simply provide a full doc in update
    field. Otherwise, provide a dict that holds the new value and field name.
    Returns the total number of documents that are updated.
    """
    @tornado.web.asynchronous
    def get(self):
        database = self.settings['db']
        query = utils.unpack_params(self)
        if 'active_only' in query:
            query['active'] = query.pop('active_only')

        num = query.pop("num", None)
        if num:
            try:
                docs = database.configuration.find().sort('time',
                                                   direction=pymongo.DESCENDING
                                                   ).limit(num)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, 'Query on config has failed',
                                             query)
        else:
            try:
                docs = database.configuration.find(query).sort('time',
                                                        direction=pymongo.DESCENDING)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, 'Query Failed: ', query)
        if docs:
            utils.return2client(self, docs)
        else:
            raise utils._compose_err_msg(500, 'No results found!')

    @tornado.web.asynchronous
    def post(self):
        database = self.settings['db']
        data = ujson.loads(self.request.body.decode("utf-8"))
        uids = []
        if isinstance(data, list):
            for d in data:
                # Ensure the active status on the new Configuration
                d['active'] = True
                d = utils.default_timeuid(d)
                try:
                    jsonschema.validate(d,
                                        utils.schemas['configuration'])
                except (ValidationError, SchemaError):
                    raise utils._compose_err_msg(400,
                                                 "Invalid schema on document(s)", d)
                uids.append(d['uid'])
                res = database.configuration.insert(d)
                database.configuration.create_index([('uid', pymongo.DESCENDING)],
                                             unique=True, background=False)
                database.configuration.create_index([('time', pymongo.DESCENDING),
                                              ('beamline_id', pymongo.DESCENDING)],
                                             unique=False, background=False)
        elif isinstance(data, dict):
            data = utils.default_timeuid(data)
            # Ensure the active status on the new Configuration
            data['active'] = True
            try:
                jsonschema.validate(data,
                                    utils.schemas['configuration'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            uids.append(data['uid'])
            res = database.configuration.insert(data)
            # if inserted, create indices that are certainly being indexed            
            if res:
                database.configuration.create_index([('uid', pymongo.DESCENDING)],
                                             unique=True, background=True)
                database.configuration.create_index([('time', pymongo.DESCENDING),
                                                     ('beamline_id', pymongo.DESCENDING)],
                                             unique=False, background=False)
        else:
            raise utils._compose_err_msg(500,
                                         status='ConfigurationHandler expects list or dict') 
        self.finish(ujson.dumps(uids))

    @tornado.web.asynchronous
    def put(self):
        database = self.settings['db']
        incoming = ujson.loads(self.request.body)
        try:
            query = incoming.pop('query')
            update = incoming.pop('update')
        except KeyError:
            raise utils._compose_err_msg(500,
                                         status='filter and update are both required fields')
        if any(x in update.keys() for x in ['uid', 'time']):
            raise utils._compose_err_msg(500,
                                   status='Time and uid cannot be updated')
        print('update query', query)
        print('update field', update)
        res = database.configuration.update_many(filter=query,
                                           update={'$set': update},
                                           upsert=False)
        self.finish(ujson.dumps(res.raw_result))

    @tornado.web.asynchronous
    def delete(self):
        database = self.settings['db']
        incoming = ujson.loads(self.request.body)
        try:
            uid_list = incoming.pop('uid_list')
        except KeyError:
            raise utils._compose_err_msg(500,
                                         status='delete require a list of uids')

        print("Delete Received list: ", uid_list)

        res = database.configuration.update_many(filter={'uid': {'$in': uid_list}},
                                                 update={'$set': {'active': False}},
                                                 upsert=False)
        self.finish(ujson.dumps(res.raw_result))


class SchemaHandler(DefaultHandler):
    """Provides the json used for schema validation provided collection name"""
    @tornado.web.asynchronous
    def get(self):
        col = utils.unpack_params(self)
        self.write(utils.schemas[col])
        self.finish()

    @tornado.web.asynchronous
    def put(self):
        raise utils._compose_err_msg(405,
                                     status='Not allowed on server')

    @tornado.web.asynchronous
    def post(self):
        raise utils._compose_err_msg(405,
                                     status='Not allowed on server')
