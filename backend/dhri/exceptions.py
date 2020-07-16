class RepositoryNotFound(Exception):
    """Raised when a provided repository is not found"""
    pass

class UnresolvedNameOrBranch(Exception):
    """Raised when a string cannot be resolved as a repository's name or branch"""
    pass

class ConstantError(Exception):
    """Raised when a constant does not fulfill the correct standard"""
    pass

class MissingCurriculumFile(Exception):
    """Raised when a repository does not contain a certain required file."""
    pass

class MissingRequiredSection(Exception):
    """Raised when a curriculum file does not contain a certain required section."""
    pass