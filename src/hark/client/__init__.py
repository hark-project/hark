import hark.log as log


class LocalClient(object):
    def __init__(self, context):
        self._context = context

    def dal(self):
        return self._context.dal

    def log(self):
        with open(self._context.log_file(), 'r') as f:
            return f.read()

    def machines(self):
        "Get all machines"
        from hark.models.machine import Machine
        return self.dal().read(Machine)

    def createMachine(self, machine):
        log.debug('Saving machine: %s', machine.json())
        self.dal().create(machine)

    def getMachine(self, name):
        "Get a machine by name."
        import hark.exceptions
        from hark.models.machine import Machine

        m = self.dal().read(Machine, constraints={"name": name})
        if len(m) == 0:
            raise hark.exceptions.MachineNotFound
        return m[0]

    def portMappings(self, name=None, machine_id=None):
        "Get all port mappings"
        from hark.models.portmapping import PortMapping
        constraints = {}
        if name is not None:
            constraints['name'] = name
        if machine_id is not None:
            constraints['machine_id'] = machine_id

        return self.dal().read(PortMapping, constraints=constraints)

    def createPortMapping(self, mapping):
        log.debug('Saving port mapping: %s', mapping)
        self.dal().create(mapping)

    def images(self):
        "Return the list of locally cached images"
        return self._context.image_cache().images()

    def imagePath(self, image):
        "Get the full file path to an image"
        return self._context.image_cache().full_image_path(image)

    def saveImageFromFile(self, image, source):
        self._context.image_cache().saveFromFile(image, source)

    def saveImageFromUrl(self, image, url):
        import hark.util.download
        import requests
        resp = requests.get(url, stream=True)
        f = open(self.imagePath(image), 'wb')

        try:
            hark.util.download.responseToFile(
                'Downloading:', resp, f)
        finally:
            resp.close()
            f.close()


class ImagestoreClient(object):
    def __init__(self, url):
        import requests
        import hark.imagestore

        self.session = requests.session()
        self.base_url = url
        self.session.headers['Accept'] = 'application/json'
        self.urls = hark.imagestore.URLS

    def _full_url(self, url):
        return "%s/%s" % (self.base_url, url)

    def _get(self, url):
        response = self.session.get(self._full_url(url))
        response.raise_for_status()
        return response.json()

    def images(self):
        from hark.models.image import Image
        js = self._get(self.urls['images'])
        return [Image(**o) for o in js]

    def image_url(self, image):
        url = self.urls['image'].format(**image)
        js = self._get(url)
        return js['url']
