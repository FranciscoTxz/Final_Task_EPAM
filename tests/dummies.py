import io


class DummyUser:
    def __init__(self, id: int, name: str, password: str):
        self.id = id
        self.name = name
        self.password = password


class DummyProject:
    def __init__(self, id: int, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description


class DummyCreateProject:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class DummyUserProject:
    def __init__(self, is_owner: bool, project: DummyProject):
        self.is_owner = is_owner
        self.project = project


class DummyUserProjectCreate:
    def __init__(self, user_id: int, project_id: int, is_owner: bool):
        self.user_id = user_id
        self.project_id = project_id
        self.is_owner = is_owner


class DummyProjectUpdate:
    def __init__(self, name: str | None, description: str | None):
        self.name = name
        self.description = description


class DummyDocument:
    def __init__(self, id: int, name: str, url: str):
        self.id = id
        self.name = name
        self.url = url


class DummyCreateDocument:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url


class DummyUploadFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = io.BytesIO(content)
        self.content_type = "application/octet-stream"


class DummyDocumentComplex:
    def __init__(self, id: int, name: str, url: str, project_id: int):
        self.id = id
        self.name = name
        self.url = url
        self.project_id = project_id


class DummyDocumentUpdate:
    def __init__(self, name: str = None, url: str = None):
        self.name = name
        self.url = url
