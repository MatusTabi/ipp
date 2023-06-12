import xml.etree.ElementTree as ET
import sys, getopt, re
import os.path  
   

"""
Trieda implementujuca vsetky instrukcia podla navrhoveho vzoru Singleton (Jedinacik).
Pomocou slovniku a prislusnej metody implementuje danu instrukciu.
Metoda obsahuje atributy:
instructionList - zoznam vsetkych instrukcii
callStack - zasobnik pre CALL instrukciu, kam sa zapisuju indexi, kam sa treba vratit
dataStack - zasobnik hodnot pre PUSHS a POPS instrukcie
stackGF - zasobnik pre globalny ramec
insDictionary - slovnik vsetkych instrukcii a prisluchajucich metod
"""
class Dictionary:
    __instance = None
    def __init__(self, instructionList: list):
        if Dictionary.__instance != None:
            raise Exception("Trieda je jedinacik, nie je mozne ju znova instanciovat\n")
        else:        
            self.instructionList = instructionList
            self.callStack = []
            self.dataStack = []
            self.stackGF = []
            self.sortInstructions()
            self.insDictionary = {
                'DEFVAR': self.defvar,
                'MOVE': self.move,
                'WRITE': self.write,
                'ADD': self.add,
                'SUB': self.sub,
                'MUL': self.mul,
                'IDIV': self.idiv,
                'EQ': self.eq,
                'LT': self.lt,
                'GT': self.gt,
                'AND': self.andI,
                'OR': self.orI,
                'NOT': self.notI,
                'JUMP': self.jump,
                'JUMPIFEQ': self.jumpifeq,
                'JUMPIFNEQ': self.jumpifneq,
                'CALL': self.call,
                'RETURN': self.returnI,
                'EXIT': self.exitI,
                'TYPE': self.typeI,
                'CONCAT': self.concat,
                'STRLEN': self.strlen,
                'INT2CHAR': self.int2char,
                'STRI2INT': self.stri2int,
                'GETCHAR': self.getchar,
                'SETCHAR': self.setchar,
                'PUSHS': self.pushs,
                'POPS': self.pops,
                'READ': self.read,
                'CREATEFRAME': self.createframe,
                'PUSHFRAME': self.pushframe,
                'POPFRAME': self.popframe,
                'LABEL': self.label
            }
            Dictionary.__instance = self
    
    @staticmethod
    def getInstance() -> 'Dictionary':
        if Dictionary.__instance == None:
            Dictionary()
        return Dictionary.__instance
    """
    Metoda DEFVAR instrukcie.
    Podla ramca skontroluje, ci bola premenna uz raz deklarovana.
    Ak nebola, priradi ju do prislusneho zasobniku pre ramce.
    """
    def defvar(self, ins: ET.Element) -> None:
        match ins.argumentList[-1].value.scope:
            case 'GF':
                if findVariableRedeclared(self.instructionList[ins.index + 1:], ins.argumentList[-1], self.stackGF):
                    exit(52)
                self.stackGF.append(ins.argumentList[-1].value.variableName)
            case 'TF':
                try: 
                    if findVariableRedeclared(self.instructionList[ins.index + 1:], ins.argumentList[-1], self.stackTF, 'stackTF'):
                        exit(52)
                except AttributeError:
                    exit(55)
                try: self.stackTF.append(ins.argumentList[-1].value.variableName)
                except IndexError:
                    exit(55)
            case 'LF':
                try:
                    if findVariableRedeclared(self.instructionList[ins.index + 1:], ins.argumentList[-1], self.stackLF[-1], 'stackLF'):
                        exit(52)
                except AttributeError:
                    exit(55)
                try: self.stackLF[-1].append(ins.argumentList[-1].value.variableName)
                except IndexError:
                    exit(55)
            case _:
                exit(32)
    """
    Metoda MOVE instrukcie.
    Vyhlada danu premennu a priradi jej obsah, typ a bool hodnotu.
    """
    def move(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        if isinstance(ins.argumentList[-1].value, Bool) and not ins.argumentList[-1].value.booleanValue:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(ins.argumentList[-1].value.getValue(), 
                                                                                ins.argumentList[-1].getArgType(), False)
            return    
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(ins.argumentList[-1].value.getValue(), 
                                                                            ins.argumentList[-1].getArgType(), True)
    """
    Metoda WRITE instrukcie.
    Vypise obsah instrukcie.
    """
    def write(self, ins: ET.Element) -> None:
        if isinstance(ins.argumentList[-1].value, Variable):
            self.isDeclared(ins.argumentList[-1]).argumentList[-1].value.writeValue()
            return
        ins.argumentList[-1].value.writeValue()
    """
    Metoda ADD instrukcie.
    Skontroluje, ci su oba operandy typu int a vykona ich sucet.
    """
    def add(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        self.isTypeInt(ins)
        result = ins.argumentList[1].addition(ins.argumentList[2].value.getValue())
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metoda SUB instrukcie.
    Skontroluje, ci su oba operandy typu int a vykona ich odcitanie.
    """
    def sub(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        self.isTypeInt(ins)
        result = ins.argumentList[1].substraction(ins.argumentList[2].value.getValue())
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metoda MUL instrukcie.
    Skontroluje, ci su oba operandy typu int a vykona ich nasobenie.
    """
    def mul(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        self.isTypeInt(ins)
        result = ins.argumentList[1].multiplication(ins.argumentList[2].value.getValue())
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metoda IDIV instrukcie.
    Skontroluje, ci su oba operandy typu int a vykona ich celociselne delenie.
    """
    def idiv(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        self.isTypeInt(ins)
        result = ins.argumentList[1].intDivision(ins.argumentList[2].value.getValue())
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metooda EQ instrukcie.
    Podla vyslednej hodnoty porovnania dvoch argumentov je do premennej priradena vysledna bool hodnota.
    """
    def eq(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] == ins.argumentList[2]
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda LT instrukcie.
    Vykona sa porovnanie dvoch argumentov a zapise sa vysledna bool hodnota.
    """
    def lt(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] < ins.argumentList[2]
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda GT instrukcie.
    Vykona sa porovnanie dvoch argumentov a zapise sa vysledna bool hodnota.
    """
    def gt(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] > ins.argumentList[2]
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda AND instrukcie.
    Vykona logicky and nad bool hodnotami a zapise do premennej vyslednu hodnotu.
    """
    def andI(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] & ins.argumentList[2]
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda OR instrukcie.
    Vykona logicky or nad bool hodnotami a zapise do premennej vyslednu hodnotu.
    """
    def orI(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] | ins.argumentList[2]
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda NOT instrukcie.
    Vykona negaciu nad bool hodnotami a zapise do premennej vyslednu hodnotu.
    """
    def notI(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = (-ins.argumentList[1])
        if result == True:
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('true', 'bool', True)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
    """
    Metoda JUMP instrukcie.
    Metoda vyhlada navestie, na ktore je treba skocit a vykona instrukcie za tymto navestim.
    """
    def jump(self, ins: ET.Element) -> None:
        found = self.findLabel(ins.argumentList[-1].value.content)
        self.evokeInstruction(found)
    """
    Metoda JUMPIFEQ instrukcie.
    Metoda porovna dva argumenty a v pripade pravdivej hodnoty vyhlada navestie a vykona instrukcie za nim.
    """
    def jumpifeq(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] == ins.argumentList[2]
        if result == True:
            found = self.findLabel(ins.argumentList[0].value.content)
            self.evokeInstruction(found)
    """
    Metoda JUMPIFEQ instrukcie.
    Metoda porovna dva argumenty a v pripade pravdivej hodnoty vyhlada navestie a vykona instrukcie za nim.
    """
    def jumpifneq(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = not ins.argumentList[1] == ins.argumentList[2]
        if result == True:
            found = self.findLabel(ins.argumentList[0].value.content)
            self.evokeInstruction(found)
    """
    Metoda CALL instrukcie.
    Metoda vyhlada navestie, na ktore chce skocit. Vlozi svoju poziciu do zasobniku skokovych instrukcii
    a vykona instrukcie za navestim.
    """
    def call(self, ins: ET.Element) -> None:
        found = self.findLabel(ins.argumentList[-1].value.content)
        self.callStack.append(ins.index + 1)
        self.evokeInstruction(found)
    """
    Metoda RETURN instrukcie.
    Metoda vytiahne zo zasobniku index a vykona instrukcie za nim.
    """
    def returnI(self, ins: ET.Element) -> None:
        try: returnIndex = self.callStack.pop()
        except IndexError:
            exit(56)
        self.evokeInstruction(returnIndex)
    """
    Metoda EXIT instrukcie.
    Metoda skontroluje typ a interval argumentu a v pripade pravdy vykona exit.
    """
    def exitI(self, ins: ET.Element) -> None:
        if isinstance(ins.argumentList[-1].value, Integer) and ins.argumentList[-1].value.isinInterval():
            exit(ins.argumentList[-1].value.retype())
        exit(53)
    """
    Metoda TYPE instrukcie.
    Metoda kontroluje, ci je posledny argument premenna alebo iny symbol a podla typu priradi do premennej vysledny typ.
    """
    def typeI(self, ins: ET.Element) -> None:
        firstArg = self.isDeclared(ins.argumentList[0])
        if isinstance(ins.argumentList[-1].value, Variable):
            secondArg = self.isDeclared(ins.argumentList[-1])
            if not hasattr(secondArg.argumentList[-1].value, 'content'):
                firstArg.argumentList[-1].value.setValue('', 'string', True)
                return
            firstArg.argumentList[-1].value.setValue(secondArg.argumentList[-1].value.dataType, 'string', True)
            return
        firstArg.argumentList[-1].value.setValue(ins.argumentList[-1].argType, 'string', True)
    """
    Metoda CONCAT instrukcie.
    Metoda skonkatenuje dva retazce.
    """    
    def concat(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        result = ins.argumentList[1] + ins.argumentList[2]
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'string', True)
    """
    Metoda STRLEN instrukcie.
    Metoda zisti dlzku retazca.
    """
    def strlen(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        try: result = ins.argumentList[-1].value.getLength()
        except AttributeError:
            exit(53)
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metoda INT2CHAR instrukcie.
    Metoda vezme argument instrukcie a zmeni ho na jeho ascii podobu.
    """
    def int2char(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        try: result = ins.argumentList[-1].value.toChar()
        except AttributeError:
            exit(53)
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'string', True)
    """
    Metoda STRI2INT instrukcie:
    Metoda vezme index a premeni charakter na indexe na jeho ascii hodnotu.
    """
    def stri2int(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        try: result = ins.argumentList[1].value.toInt(ins.argumentList[-1].value)
        except AttributeError:
            exit(53)
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'int', True)
    """
    Metoda GETCHAR instrukcie:
    Metoda vezme index a do premennej zapise znak na tomto indexe.
    """
    def getchar(self, ins: ET.Element) -> None:
        self.updateArguments(ins)
        try: result = ins.argumentList[1].value.getChar(ins.argumentList[-1].value)
        except AttributeError:
            exit(53)
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'string', True)
    """
    Metoda SETCHAR instrukcie.
    Metoda vezme index a prvy charakter v poslednom argumente a vo vyslednom retazci nahradi znak na indexe.
    """
    def setchar(self, ins: ET.Element) -> None:
        self.updateArguments(ins, 0)
        result = ins.argumentList[0].value.setCharacter(ins.argumentList[1].value, ins.argumentList[2].value.getFirstChar())
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(result, 'string', True)
    """
    Metoda PUSHS instrukcie:
    Metoda vlozi na zasobnik argument.
    """
    def pushs(self, ins: ET.Element) -> None:
        self.updateArguments(ins, 0)
        if isinstance(ins.argumentList[-1].value, Label):
            exit(53) 
        self.dataStack.append(ins.argumentList[-1])
    """
    Metoda POPS instrukcie.
    Metoda vytiahne prvy element zo zasobnika a vlozi data do premennej.
    """
    def pops(self, ins: ET.Element) -> None:
        try: tempArgument = self.dataStack.pop()
        except IndexError:
            exit(56)
        if isinstance(tempArgument.value, Variable):    
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(tempArgument.value.content,
                                                                                 tempArgument.value.dataType,
                                                                                 tempArgument.value.booleanValue)
            return
        self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(tempArgument.value.content,
                                                                             tempArgument.argType,
                                                                             tempArgument.value.booleanValue)
    """
    Metoda READ instrukcie.
    Metoda v precita riadok zo suboru alebo standardneho vstupu a podla typu pripadi hodnotu do premennej.
    """
    def read(self, ins: ET.Element) -> None:
        if readInput == '':
            userInput = input()
        else:
            file = open(readInput)
            userInput = file.readline().replace('\n', '')
        try:
            if ins.argumentList[-1].value.content == 'bool':
                if userInput == 'true':
                    self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(userInput, 'bool', True)
                    return
                if userInput == '':
                    self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('', 'nil', False)
                    return
                self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('false', 'bool', False)
                return
            elif ins.argumentList[-1].value.content == 'int':
                try: self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(int(userInput), 'int', True)
                except ValueError:
                    self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('', 'nil', False)
                return
            elif ins.argumentList[-1].value.content == 'string':
                self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue(userInput, 'string', True)
                return
            self.isDeclared(ins.argumentList[0]).argumentList[-1].value.setValue('', 'nil', False)
            return
        except AttributeError:
            exit(32)
    """
    Metoda CREATEFRAME instrukcie.
    Vytvori prazdny zasobnik pre TF.
    """
    def createframe(self, ins: ET.Element) -> None:
        self.stackTF = []
    """
    Metoda PUSHFRAME instrukcie.
    Metoda skontroluje, ci je definovany LF, ak nie je, vytvori ho. Inak na prve miesto v zasobniku LF priradi obsah TF zasobniku.
    """
    def pushframe(self, ins: ET.Element) -> None:
        if not hasattr(self, 'stackLF'):
            self.stackLF = []
        try: self.stackLF.append(self.stackTF)
        except AttributeError:
            exit(55)
        delattr(self, 'stackTF')
    """
    Metoda POPFRAME instrukcie.
    Zo zasobniku LF vytiahne hodnoty a priradi ich naspat do TF.
    """
    def popframe(self, ins: ET.Element) -> None:
        self.stackTF = []
        try: self.stackTF.append(self.stackLF[-1].pop())
        except AttributeError:
            exit(55)
    """
    Metoda LABEL instrukcie.
    Metoda skontroluje, ci neboli redefinovane navestia.
    """
    def label(self, ins: ET.Element) -> None:
        for label in self.instructionList[ins.index + 1:]:
            if label.name == 'LABEL' and label.argumentList[-1].value.content == ins.argumentList[-1].value.content:
                exit(52)
    """
    Pomocna metoda, ktora zoradi instrukcie podla order a nastavi indexy.
    """
    def sortInstructions(self) -> None:
        self.instructionList.sort(key=lambda ins: int(ins.order))
        for index, ins in enumerate(self.instructionList):
            ins.setIndex(index)
    """
    Metoda, ktora vyvola metody prisluchajuce ku instrukciam.
    """
    def evokeInstruction(self, startingIndex: int) -> None:
        for ins in self.instructionList[startingIndex:]:
            if ins.getInstructionName() in self.insDictionary:
                self.insDictionary.get(ins.getInstructionName())(ins)
        exit(0)
    """
    Kontrola, ci bola premenna deklarovana.
    """
    def isDeclared(self, argument) -> 'Instruction':
        match argument.value.scope:
            case 'GF':
                found = findVariable(self.instructionList, argument, self.stackGF)
            case 'TF':
                try: found = findVariable(self.instructionList, argument, self.stackTF, 'stackTF')
                except AttributeError:
                    exit(55)
            case 'LF':
                try: found = findVariable(self.instructionList, argument, self.stackLF[-1], 'stackLF')
                except AttributeError:
                    exit(55)
            case _:
                exit(32)
        if not found:
            exit(54)
        return found
    """
    Metoda, ktora aktualizuje premenne a ich hodnoty v instrukciach.
    """
    def updateArguments(self, ins: ET.Element, index: int = 1) -> None:
        for argument in ins.argumentList[index:]:
            if isinstance(argument.value, Variable):
                found = self.isDeclared(argument)
                
                if found.argumentList[-1].value.booleanValue == False:
                    argument.value.setValue(found.argumentList[-1].value.content, found.argumentList[-1].value.dataType, False)    
                else:
                    argument.value.setValue(found.argumentList[-1].value.content, found.argumentList[-1].value.dataType, True)
    """
    Kontrola, ci argument je typu int.
    """
    def isTypeInt(self, ins: ET.Element) -> None:
        for argument in ins.argumentList[1:]:
            if isinstance(argument.value, Variable) and argument.value.dataType == 'int':
                continue
            elif not isinstance(argument.value, Integer):
                exit(53)
    """
    Vyhladanie navestia a vratenia indexu.
    """
    def findLabel(self, labelName: str) -> None:
        for index, label in enumerate(self.instructionList):
            if label.name == 'LABEL' and label.argumentList[-1].value.content == labelName:
                return index + 1
        exit(52)
"""
Trieda pre kazdu jednu instrukciu. V hlavnom cykle programu sa vytvara tato trieda pre kazdu instrukciu
a priraduju sa k nej potrebne hodnoty.
Metoda obsahuje atributy:
name - meno instrukcie
order - poradie instrukcie
argumentList - zoznam objektov Argument prisluchajucich instrukcii
index - index instrukcie
"""
class Instruction:
    def __init__(self, elem: ET.Element) -> None:                                   
        self.name = str(elem.attrib['opcode'])
        self.order = int(elem.attrib['order'])
        self.argumentList = []

    """
    Ziskanie nazvu instrukcie.
    """
    def getInstructionName(self) -> str:
        return self.name
    """
    Ziskanie mena premennej v instrukcii.
    """
    def getVarName(self) -> str:
        if self.argumentList and isinstance(self.argumentList[0].value, Variable):
            return self.argumentList[0].value.variableName 
    """
    Ziskanie obsahu posledneho argumentu.
    """
    def getValue(self) -> any:
        return self.argumentList[-1].value.content
    """
    Pridanie argumentu do zoznamu argumentov a rozoznanie typu argumentu (var, string, int, type).
    """
    def addArgument(self, arg: ET.Element) -> None:
        self.argumentList.append(Argument(arg))                                 
        self.argumentList[-1].recognizeArg(arg)
    """
    Pomocna metoda na zoradenie argumentov podla cisla argumentov.
    """
    def sortArguments(self) -> None:
        self.argumentList.sort(key=lambda argument: argument.argumentNo)
    """
    Nastavenie indexu instrukcie.
    """
    def setIndex(self, index: int) -> None:
        self.index = index
"""
Trieda pre argumenty instrukcii. 
Metoda obsahuje atributy:
argumentNo - poradie argumentu
argType - typ argumentu
value - prisluchajuci objekt argumentu (Variable, Integer, String, Bool, Label)
""" 
class Argument:
    def __init__(self, elem: ET.Element) -> None:
        self.argumentNo = int(re.findall(r'\d+', elem.tag)[0])
        self.argType = str(elem.attrib['type'])
    """
    Prepisanie vstavanych metod pre argumenty a spravnu kompatibilitu pri porovnavani argumentov.
    """
    def __eq__(self, other) -> bool:
        if self.argType == 'nil' or other.argType == 'nil':
            return self.value.content == other.value.content
        if self.argType == 'var' or other.argType == 'var':
            return self.value == other
        if self.argType == other.argType:
            return self.value.retype() == other.value.retype()
        exit(53)
    
    def __lt__(self, other) -> bool:
        if self.argType == 'nil' or other.argType == 'nil':
            exit(53)
        if self.argType == 'var' or other.argType == 'var':
            return self.value < other
        if self.argType == other.argType:
            return self.value.retype() < other.value.retype()
    
    def __gt__(self, other) -> bool:
        if self.argType == 'nil' or other.argType == 'nil':
            exit(53)
        if self.argType == 'var' or other.argType == 'var':
            return self.value > other
        if self.argType == other.argType:
            return self.value.retype() > other.value.retype()

    def __and__(self, other) -> bool:
        if self.argType == 'var':
            return self.value & other
        if self.argType == 'bool' and other.argType == 'var':
            return self.value.booleanValue & other.value.booleanValue
        if self.argType == 'bool' and other.argType == 'bool':
            return self.value.booleanValue & other.value.booleanValue
        exit(53)
    
    def __or__(self, other) -> bool:
        if self.argType == 'var' or other.argType == 'var':
            return self.value | other
        if self.argType == 'bool' and other.argType == 'bool':
            return self.value.booleanValue | other.value.booleanValue
        exit(53)
    
    def __neg__(self) -> bool:
        if self.argType == 'var':
            return (-self.value)
        if self.argType == 'bool':
            return not self.value.booleanValue 
        exit(53)
        
    def __add__(self, other) -> str:
        if isinstance(self.value, Variable):
            return self.value + other
        if self.argType == 'string' and (isinstance(other.value, Variable) or isinstance(other.value, String)):
            return self.value.content + other.value.content
        exit(53)
    """
    Metoda, ktora rozozna, o aky typ argumentu ide a podla tohto typu vytvori potrebnu instanciu (Variable, ...).
    """
    def recognizeArg(self, elem: ET.Element) -> None:
        if self.argType == 'var':
            self.value = Variable(elem)
        elif self.argType == 'string':
            self.value = String(elem)
        elif self.argType == 'int':
            self.value = Integer(elem)
        elif self.argType == 'nil':
            self.value = String(elem)
            self.value.setValue()
        elif self.argType == 'bool':
            self.value = Bool(elem)
        elif self.argType == 'label':
            self.value = Label(elem)
        elif self.argType == 'type':
            self.value = String(elem)
    """
    Ziskanie typu argumentu.
    """
    def getArgType(self) -> str:
        return self.argType
    """
    Aritmeticke metody nad argumentami.
    """
    def addition(self, secondValue: int) -> int:
        return int(self.value.content) + int(secondValue)
    
    def substraction(self, secondValue: int) -> int:
        return int(self.value.content) - int(secondValue)
    
    def multiplication(self, secondValue: int) -> int:
        return int(self.value.content) * int(secondValue)
    
    def intDivision(self, secondValue: int) -> int:
        try: return int(int(self.value.content) / int(secondValue))
        except ZeroDivisionError:
            exit(57)
        
"""
Trieda pre typ var.
Metoda obsahuje atributy:
scope - ramec premennej
variableName - meno premennej
dataType - datovy typ premennej
booleanValue - bool hodnota premennej
content - obsah premennej
"""
class Variable:
    """
    Konstruktor premennej.
    Vytvori premennu, ktora ma svoj scope a nazov.
    """
    def __init__(self, elem: ET.Element) -> None:
        splitted = elem.text.split('@')
        self.scope = str(splitted[0])
        self.variableName = str(splitted[1])
        self.dataType = ''
        self.booleanValue = False
    """
    Prepisovanie metod pre spravne porovnavanie argumentov.
    """
    def __eq__(self, other) -> bool:
        if isinstance(other.value, Variable) and self.dataType == other.value.dataType:
            return self.content == other.value.content
        if self.dataType == other.argType:
            return self.content == other.value.retype()
        exit(53)
    
    def __lt__(self, other) -> bool:
        if self.dataType == 'nil' or other.argType == 'nil':
            exit(53)
        if isinstance(other.value, Variable) and other.value.dataType == 'nil':
            exit(53)
        if isinstance(other.value, Variable) and self.dataType == other.value.dataType:
            return self.content < other.value.content
        if self.dataType == other.argType:
            return self.content < other.value.retype()
        exit(53)
    
    def __gt__(self, other) -> bool:
        if self.dataType == 'nil' or other.argType == 'nil':
            exit(53)
        if isinstance(other.value, Variable) and other.value.dataType == 'nil':
            exit(53)
        if isinstance(other.value, Variable) and self.dataType == other.value.dataType:
            return self.content > other.value.content
        if self.dataType == other.argType:
            return self.content > other.value.retype()
        exit(53)
        
    def __and__(self, other) -> bool:
        if isinstance(other.value, Variable) and self.dataType == 'bool' and other.value.dataType == 'bool':
            return self.booleanValue & other.value.booleanValue
        if self.dataType == other.argType:
            return self.booleanValue & other.value.booleanValue
        exit(53)
        
    def __or__(self, other) -> bool:
        if isinstance(other.value, Variable) and self.dataType == 'bool' and other.value.dataType == 'bool':
            return self.booleanValue | other.value.booleanValue
        if self.dataType == other.argType:
            return self.booleanValue | other.value.booleanValue
        exit(53)
        
    def __neg__(self) -> bool:
        if self.dataType == 'bool':
            return not self.booleanValue
        exit(53) 
        
    def __add__(self, other) -> str:
        if (isinstance(other.value, Variable) and self.dataType == 'string' and other.value.dataType == 'string'
            or self.dataType == other.argType):
            return self.content + other.value.content
        exit(53)
    """
    Nastavenie obsahu, datoveho typu a bool hodnotu premennej.
    """
    def setValue(self, value: object, dataType: str, booleanValue: bool) -> None:
        self.content = value
        self.dataType = dataType
        self.booleanValue = booleanValue
    """
    Ziskanie obsahu premennej.
    """   
    def getValue(self) -> any:
        return self.content   
    """
    Vypisanie obsahu premennej
    """
    def writeValue(self) -> None:
        if hasattr(self, 'content'):
            result = re.sub(r"\\(\d\d\d)", lambda x: chr(int(x.group(1))), str(self.content))   # escape sekvencie
            print(result, end='')
            return
        exit(56)
    """
    Ziskanie dlzky retazca.
    """
    def getLength(self) -> int:
        if self.dataType == 'string':
            return len(self.content)
        exit(53)
    """
    Zmena celeho cisla na charakter podla ascii.
    """
    def toChar(self) -> str:
        if self.dataType == 'int':
            try: return chr(int(self.content))
            except ValueError:
                exit(58)
        exit(53)
    """
    Zmena charakteru na jeho ascii hodnotu.
    """
    def toInt(self, index: object) -> int:
        if self.dataType == 'string' and (isinstance(index, Integer) or (isinstance(index, Variable) and index.dataType == 'int')):
            try: return ord(self.content[index.getValue()])
            except ValueError:
                exit(58)
        exit(53) 
    """
    Ziskanie charakteru na danom indexe.
    """
    def getChar(self, index: object) -> str:
        if self.dataType == 'string' and (isinstance(index, Integer) or (isinstance(index, Variable) and index.dataType == 'int')):
            try: return self.content[index.getValue()]
            except IndexError:
                exit(58)
        exit(53)
    """
    Ziskanie prveho charakteru z retazca.
    """
    def getFirstChar(self) -> str:
        if self.dataType == 'string':
            if self.content == '':
                exit(58)
            return self.content[0]
        exit(53)
    """
    Nastavnie jedneho charakteru v retazci na dany index.
    """
    def setCharacter(self, index: object, character: str) -> str:
        if self.dataType == 'string' and (isinstance(index, Integer) or (isinstance(index, Variable) and index.dataType == 'int')):
            try: newContent = self.content.replace(self.content[index.getValue()], character)
            except IndexError:
                exit(58)
            return newContent
        exit(53)
"""
Trieda reprezentujuca retazec.
Metoda obsahuje atributy:
content - obsah retazca
booleanValue - bool hodnotu
"""
class String:
    def __init__(self, elem: ET.Element) -> None:
        if elem.text == None:
            self.content = ''
            return
        self.content = elem.text.strip()
        self.booleanValue = True
    """
    Ziskanie obsahu retazca
    """
    def getValue(self) -> str:
        return str(self.content)
    """
    Nastavenie prazdneho retazca.
    """
    def setValue(self) -> None:
        self.content = ''
    """
    Pretypovanie retazca.
    """
    def retype(self) -> str:
        return str(self.content)
    """
    Vypis obsahu retazca.
    """
    def writeValue(self) -> None:
        result = re.sub(r"\\(\d\d\d)", lambda x: chr(int(x.group(1))), self.content)
        print(result, end='')
    """
    Ziskanie dlzky retazca.
    """
    def getLength(self) -> int:
        return len(self.content)
    """
    Zmenenie charakteru na danom indexe na cislenu hodnotu.
    """
    def toInt(self, index: object) -> int:
        if isinstance(index, Integer) or isinstance(index, Variable):
            try: return ord(self.content[index.getValue()])
            except IndexError:
                exit(58)
        exit(53)
    """
    Ziskanie charakteru v retazci na danom indexe
    """
    def getChar(self, index: object) -> str:
        if isinstance(index, Integer) or isinstance(index, Variable):
            try: return self.content[index.getValue()]
            except IndexError:
                exit(58)
        exit(53)
    """
    Ziskanie prveho prvku z retazca.
    """
    def getFirstChar(self) -> str:
        return self.content[0]
"""
Trieda reprezentujuca cele cislo.
Metoda obsahuje atributy:
booleanValue - bool hodnota
content - obsah
""" 
class Integer:
    def __init__(self, elem: ET.Element) -> None:
        self.booleanValue = True
        try: self.content = int(elem.text)
        except ValueError:
            exit(32)
    """
    Prepisovanie vstavanych metod pre pracu s porovnavaniami.
    """
    def __eq__(self, other) -> bool:
        if isinstance(other.value, Variable) and 'int' == other.value.dataType:
            return self.retype() == other.value.content
        if 'int' == other.argType:
            return self.retype() == other.value.content
    
    def __lt__(self, other) -> bool:
        if isinstance(other.value, Variable) and 'int' == other.value.dataType:
            return self.retype() < other.value.content
        if 'int' == other.argType:
            return self.retype() < other.value.content
    
    def __gt__(self, other) -> bool:
        if isinstance(other.value, Variable) and 'int' == other.value.dataType:
            return self.retype() > other.value.content
        if 'int' == other.argType:
            return self.retype() > other.value.content
    """
    Ziskanie obsahu.
    """
    def getValue(self) -> int:
        return int(self.content)
    """
    Pretypovanie obsahu.
    """
    def retype(self) -> int:
        return int(self.content)
    """
    Kontrola, ci sa nachadza v intervale. Pouzivanie pri EXIT instrukcii.
    """
    def isinInterval(self) -> bool:
        if 0 <= self.retype() <= 49:
            return True
        exit(57)
    """
    Vypisanie obsahu
    """
    def writeValue(self) -> None:
        # Toto tu nemusi byt pravdepodobne
        result = re.sub(r"\\(\d\d\d)", lambda x: chr(int(x.group(1))), str(self.content))
        print(result, end='')
    """
    Zmena cisla na charakter.
    """
    def toChar(self) -> str:
        try: return chr(int(self.content))   
        except ValueError:
            exit(58)
"""
Trieda reprezentujuca bool hodnotu.
Metoda obsahuje atributy:
content - string (true, false)
booleanValue - bool hodnota
"""    
class Bool:
    def __init__(self, elem: ET.Element) -> None:
        self.content = str(elem.text)
        if self.content == 'true':
            self.booleanValue = True
            return
        self.booleanValue = False   
    """
    Ziskanie obsahu.
    """
    def getValue(self) -> bool:
        return self.content
    """
    Pretypovanie hodnoty.
    """
    def retype(self) -> bool:
        return self.booleanValue
    """
    Vypisanie obsahu.
    """
    def writeValue(self) -> None:
        print(self.content, end='')
"""
Trieda reprezentujuca navestie.
Metoda obsahuje atributy:
content - obsah
""" 
class Label:
    def __init__(self, elem: ET.Element) -> None:
        self.content = str(elem.text)
"""
Kontrola, ci vstupne subory su validne.
"""
def fileCheck(args) -> None:
    if not (os.path.isfile(args)):
        exit(11)
"""
Vyhladanie premennej v zozname instrukcii.
"""
def findVariable(instructionList: list, argument: Argument, scopeStack: list, tempScope: str = 'stackGF') -> 'Instruction':
    if not hasattr(Dictionary.getInstance(), tempScope):
        exit(55)
    return next((variable for variable in instructionList if variable.getVarName() == argument.value.variableName
        and variable.getInstructionName() == 'DEFVAR' and argument.value.variableName in scopeStack), False)
"""
Vyhladanie premennej v zozname instrukcii. Pouzivane pri kontrole, ci bola premenna uz raz deklarovana.
"""
def findVariableRedeclared(instructionList: list, argument: Argument, scopeStack: list, tempScope: str = 'stackGF') -> 'Instruction':
    if not hasattr(Dictionary.getInstance(), tempScope):
        exit(55)
    return next((variable for variable in instructionList if variable.getVarName() == argument.value.variableName
        and variable.getInstructionName() == 'DEFVAR' and not argument.value.variableName in scopeStack), False)
"""
Handlovanie chyby pri getopt
"""
try:
    options, args = getopt.getopt(sys.argv[1:], "", ["help", "source=", "input="])
except getopt.GetoptError:
    exit(11)

source = ''
readInput = ''

for opt, args in options:
    if opt == '--help':
        print('Pomocka')
    elif opt == '--source':
        source = args
        fileCheck(args)
    elif opt == '--input':
        readInput = args
        fileCheck(args)
if len(sys.argv) < 2:
    exit(10)
    
"""
Hlavne telo programu. Ziska sa strom z XML vstupu a nasledne sa v jednom cykle
povkladaju vsetky instrukcie a prisluchajuce data do zoznamu instrukcii.
Nasledne sa vytvori instancia slovniku pre kazdu instrukciu a vyvola sa prva instrukcia.
"""
try: tree = ET.parse(source)
except ET.ParseError:
    exit(31)

root = tree.getroot()
instructionList = []

for instruction in root:
    newInstruction = Instruction(instruction)
    for arg in instruction:
        newInstruction.addArgument(arg)
    newInstruction.sortArguments()
    instructionList.append(newInstruction)


instructionDictionary = Dictionary(instructionList)
instructionDictionary.evokeInstruction(0)
