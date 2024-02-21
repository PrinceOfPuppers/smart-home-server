from dataclasses import dataclass

# error occured [num] times in a row (ie networking errors)
@dataclass
class ConseqError:
    name:str
    num:int = 1
    info:str = ""

    def __str__(self):
        if self.info:
            return f'{self.name} Chain: {self.num}, {self.info}\n'
        return f'{self.name} Chain: {self.num}\n'


# true false, was there an error
@dataclass
class FlagError:
    name:str
    info:str = ""

    def __str__(self):
        if self.info:
            return f'{self.name}: {self.info}\n'
        return f'{self.name}\n'

#essentially a set of flags (without info)
@dataclass
class SetError:
    name:str
    errors:set
    def __str__(self):
        s = f'{self.name} Set:\n'
        for err in self.errors:
            s+= f"  {err}\n"
        return s

currentErrors = {
}

def incConseqError(name:str, info:str = ""):
    if name in currentErrors:
        assert isinstance(currentErrors[name], ConseqError)
        currentErrors[name].num += 1
        if info:
            currentErrors[name].info = info
        return

    currentErrors[name] = ConseqError(name, info=info)

def clearConseqError(name:str):
    if name in currentErrors:
        currentErrors.pop(name)

def addFlagError(name:str, info:str=""):
    if name in currentErrors:
        if info:
            currentErrors[name].info = info
        return
    currentErrors[name] = FlagError(name,info)

def clearFlagError(name:str):
    if name in currentErrors:
        currentErrors.pop(name)

def addSetError(name:str, err:str):
    if name not in currentErrors:
        currentErrors[name] = SetError(name, set())
    if err not in currentErrors[name].errors:
        currentErrors[name].errors.add(err)

def clearErrorInSet(name:str, err:str):
    if name not in currentErrors:
        return
    currentErrors[name].errors.discard(err)
    if len(currentErrors[name].errors) == 0:
        currentErrors.pop(name)

def clearErrorSet(name:str):
    if name not in currentErrors:
        return
    currentErrors[name].pop(name)

def clearAllErrors():
    currentErrors.clear()


def getErrorStrAndBool():
    s = ""

    for val in currentErrors.values():
        s += str(val)

    if not s:
        return "No Errors", False
    return s, True
