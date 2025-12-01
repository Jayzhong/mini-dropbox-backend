class FileDomainException(Exception):
    """Base exception for File domain errors."""
    pass

class FolderNotFound(FileDomainException):
    """Raised when a requested folder does not exist."""
    pass

class FileNotFound(FileDomainException):
    """Raised when a requested file does not exist."""
    pass

class FolderAlreadyExists(FileDomainException):
    """Raised when attempting to create a folder that already exists in the same parent location."""
    pass

class ShareLinkNotFound(FileDomainException):
    """Raised when a share link cannot be found."""
    pass

class ShareLinkDisabled(FileDomainException):
    """Raised when a share link is disabled."""
    pass

class ShareLinkExpired(FileDomainException):
    """Raised when a share link is expired."""
    pass
