<?php

/**
 * Nazov projektu: Analyzator kodu v IPPcode23 (parse.php)
 * Autor: Matus Tabi (xtabim01)
 */

class tokenClass extends xmlSnippet {                                                   // Trieda pre vypisovanie XML reprezentacie IPPcode23
    public function instructionVarFirst(array $buffer, int $arguments, bool $isVar) {   // Metoda, ktora vypisuje XML reprezentaciu      
        correctRegex::number_of_arguments($buffer, $arguments);                         // instrukcii, ktore nemaju dalsie argumenty
        $this->orderOpcode($buffer[0]);                                                 // Ak je $isVar true, vypisuju sa instrukcie, 
        if ($isVar === true) correctRegex::variableRegex($buffer[1]);                   // ktore maju ako prvy argument <var>
        $this->instructionArg($buffer, false, false);
    }
    public function call($buffer, $arguments) {                                         // Metoda pre skokove instrukcie a volajuce instrukcie
        correctRegex::number_of_arguments($buffer, $arguments);
        $this->orderOpcode($buffer[0]);
        correctRegex::label($buffer[1]);
        $this->instructionArg($buffer, true, false);
    }
    public function var_type($buffer, $arguments) {                                     // Metoda pre instrukciu READ
        correctRegex::number_of_arguments($buffer, $arguments); 
        $this->orderOpcode($buffer[0]);
        correctRegex::variableRegex($buffer[1]);
        $this->instructionArg($buffer, false, true);
    }
}

class correctRegex {                                            // Trieda obsahujuca metody na kontrolu regexov a poctu argumentov instrukcii
    public static function variableRegex(string $variable) {                            
        if (!preg_match("/(LF|GF|TF)@[A-Za-z_\-$&%*!?][A-Za-z0-9_\-$&%*!?]*/", $variable)) {
            exit(23);
        }
    }
    public static function label(string $label) {
        if (!preg_match("/^[A-Za-z_\-$&%*!?][A-Za-z0-9_\-$&%*!?]*$/", $label)) {
            exit(23);
        }
    }
    public static function type(string $type) {
        if (!preg_match("/^(string|bool|int)$/", $type)) {
            exit(23);
        }
    }
    public static function number_of_arguments($buffer, $number) {
        if (count($buffer) - 1 != $number) {
            exit(23);
        }
    }
}

class xmlSnippet extends SimpleXMLElement {
    protected static $instructionCount = 0;
    protected static $argCount = 0;
    protected static $instruction;
    public function orderOpcode(string $instructionName) {                          
        self::$instruction = $this->addChild('instruction', ' ');
        self::$instruction->addAttribute('order', strval(++self::$instructionCount));
        self::$instruction->addAttribute('opcode', strtoupper($instructionName));
    }
    public function instructionArg(array $buffer, bool $isLabel, bool $isType) {
        if ($isLabel === TRUE) {
            correctRegex::label($buffer[1]);
            $arg = self::$instruction->addChild('arg'.strval(++self::$argCount));
            $arg[0] = $buffer[1];
            $arg->addAttribute('type', 'label');
            $buffer = array_slice($buffer, 1);
        }
        foreach ($buffer as $index => $string) {
            if (empty($buffer[$index + 1])) {
                self::$argCount = 0;
                break;
            }
            $arg = self::$instruction->addChild('arg'.strval(++self::$argCount));
            $arg[0] = self::symb($buffer[$index + 1])[1];
            $arg->addAttribute('type', self::symb($buffer[$index + 1])[0]);
            if ($isType === TRUE) break;
        }
        if ($isType === TRUE) {
            correctRegex::type($buffer[2]);
            $arg = self::$instruction->addChild('arg'.strval(++self::$argCount));
            $arg[0] = $buffer[2];
            $arg->addAttribute('type', 'type');
            self::$argCount = 0;
        }
    }
    static public function symb(string $argument) {                     // Metoda kontrolujuca <symb> argument
        $symb = explode('@', $argument);
        switch($symb[0]) {
            case "int":
                if (!preg_match("/^[-+]?[0-9]+$/", $symb[1]) and
                    !preg_match("/0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*/", $symb[1]) and
                    !preg_match("/0[oO]?[0-7]+(_[0-7]+)*/", $symb[1])) exit(23);
                return $symb;
            case "bool":
                if (!preg_match("/^(true|false)$/", $symb[1])) exit(23);
                return $symb;
            case "string":
                if (!preg_match("/^(\\\\[0-9]{3}|[^#\\\\ ])*$/", $symb[1])) exit(23);
                if (empty($symb[1])) {
                    $symb[1] = ' ';
                }
                for ($i = 1; $i < count($symb); ++$i) {
                    if (!array_key_exists($i+1, $symb)) {
                        break;
                    } 
                    $symb[1] = $symb[1]."@".$symb[$i+1];
                }
                return $symb;
            case "nil":
                if (!preg_match("/^(nil)$/", $symb[1])) exit(23);
                return $symb;
            case "LF":
            case "GF":
            case "TF":
                    $array = array(
                        0 => 'var',
                        1 => $argument,
                    );
                    return $array;
            default:
                exit(23);
        }
    }
}
if ($argc != 1 && $argc != 2) {                             // Kontrola poctu argumentov v prikazovom riadku
    exit(10);
}
if ($argc == 2) {                                           // Vypisovanie pomocky pri zadanom argumente v prikazovom riadku --help
    if (!strcmp($argv[1], "--help")) {
        echo "\n*** Analyzator kodu v IPPcode23 (parse.php) ***\n";
        echo "\n  Skript typu filer, ktory nacitava zo standartneho vstupu zdrojovy\n";
        echo "  kod v IPPcode23 a skontroluje jeho lexikalnu a syntakticku spravnost kodu.\n";
        echo "  Po uspesnej kontrole vypise XML reprezentaciu programu na standartny vystup.\n\n";
        echo "  Argumenty prikazovej riadky:\n";
        echo "      --help  :   Vypise pomocku a opis skriptu\n\n";
        exit(0);
    }
    else {
        exit(10);
    }
}

$token = new tokenClass("<?xml version=\"1.0\" encoding=\"UTF-8\" ?><program></program>");
$isHeader = false;                                  // Pomocna premenna pre odstranovanie bielych znakov a komentarov pred hlavickou
while ($isHeader != true) {                                                     
    $beforeHeader = preg_replace("/[\t\s\n]+/", '', fgets(STDIN));              // Odstranenie bielych znakov
    $whereIsComment = strpos($beforeHeader, '#');                               
    if (!empty($whereIsComment) or preg_match("/^[^#]/", $beforeHeader)) {
        $isHeader = true;
    }
}
$lang_identifier = $beforeHeader;                           // Odstranenie bielych znakov pred hlavickou
$first_line = preg_split("/\s*#/", $lang_identifier);
$lang_identifier = $first_line[0];

if (!strcmp(trim(strtoupper($lang_identifier), "\n"), ".IPPCODE23")) {          // Kontrola hlavicky
    $token->addAttribute('language', 'IPPcode23');
    while (!feof(STDIN)) {                                                      // Hlavny cyklus spracuvajuci instrukcie
        $line = trim(fgets(STDIN), "\n");                                       // Nacitanie riadku
        $buffer = preg_split("/[\t\s\n]+/", $line);                 // Odstranenie nadbytocnych bielych znakov a rozdelenie riadku na slova
        foreach ($buffer as $index => $string) {                                 // Odstranovanie komentarov
            $commentIndex = strpos($string, '#');
            if (strpos($string, '#') !== FALSE) {                                // Komentar oddeleny bielymi znakmi od argumentu alebo instrukcie
                if ($commentIndex == 0) {
                    $buffer = array_slice($buffer, 0, $index);
                }
                else {                                                           // Komentar "nalepeny" na argumente alebo instrukcii
                    $buffer[$index] = substr($string, 0, $commentIndex);
                    $buffer = array_slice($buffer, 0, $index + 1);
                }
            }
        }
        if (empty($buffer)) {
            continue;
        }       
        switch(strtoupper($buffer[0])) {                                        // Hlavny switch case pre kazdu instrukciu
            case 'POPS':                                                      
            case 'DEFVAR':
                $token->instructionVarFirst($buffer, 1, true);
                break;
            case 'MOVE':
            case 'INT2CHAR':
            case 'TYPE':
            case 'STRLEN':
            case 'NOT':
                $token->instructionVarFirst($buffer, 2, true);
                break;
            case 'POPFRAME':
            case 'CREATEFRAME':
            case 'PUSHFRAME':
            case 'RETURN':
            case 'BREAK':
                $token->instructionVarFirst($buffer, 0, false);
                break;
            case 'CALL':
            case 'LABEL':
            case 'JUMP':
                $token->call($buffer, 1);
                break;
            case 'PUSHS':
            case 'WRITE':
            case 'DPRINT':
            case 'EXIT':
                $token->instructionVarFirst($buffer, 1, false);
                break;
            case 'ADD':
            case 'SUB':
            case 'MUL':
            case 'IDIV':
            case 'LT':
            case 'GT':
            case 'EQ':
            case 'AND':
            case 'OR':
            case 'STRI2INT':
            case 'CONCAT':
            case 'GETCHAR':
            case 'SETCHAR':
                $token->instructionVarFirst($buffer, 3, true);
                break;
            case 'READ':
                $token->var_type($buffer, 2);
                break;
            case 'JUMPIFEQ':
            case 'JUMPIFNEQ':
                $token->call($buffer, 3);
                break;
            default:
                if (empty($buffer[0])) {
                    break;
                }
                else {
                    exit(22);
                }
        }
    }
}
else {
    exit(21);
}

echo $token->asXML();
return 0;
