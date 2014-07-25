import urllib
import logging
from urllib2 import urlopen, Request
from mongo_connector.doc_managers.doc_manager_base import DocManagerBase

LOG = logging.getLogger(__name__)


class DocManager(DocManagerBase):
    def __init__(self, url=None, **kwargs):
        self.url = url
        if self.url is None:
            self.url = "localhost:5000"

    def upsert(self, doc):
        url = "%s/upload?url=%s" % (self.url, urllib.quote(str(doc['_id'])))
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "http://" + url

        req = Request(url)
        req.add_header("Content-type", "application/octet-stream")
        req.add_data(doc['body'].encode('utf-8'))
        response = urlopen(req)
        LOG.info(response.read())

    def update(self, doc, update_spec):
        pass

    def remove(self, doc):
        pass

    def search(self, start_ts, end_ts):
        pass

    def commit(self):
        pass

    def get_last_doc(self):
        pass

    def stop(self):
        pass
