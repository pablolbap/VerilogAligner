import os
import re

from enum import Enum

FILE         = "test_set/simple_1.sv"
PREPROC_FILE = "test_set/simple_1__pre_proc.sv"

PATTERN = ["//", "include", "assign"]

KEYWORDS = "always"    \
    + "|" + "ifnone"       \
    + "|" + "rpmos"        \
    + "|" + "and"          \
    + "|" + "initial"      \
    + "|" + "rtran"        \
    + "|" + "assign"       \
    + "|" + "inout"        \
    + "|" + "rtranif0"     \
    + "|" + "begin"        \
    + "|" + "input"        \
    + "|" + "rtranif1"     \
    + "|" + "buf"          \
    + "|" + "integer"      \
    + "|" + "scalared"     \
    + "|" + "bufif0"       \
    + "|" + "join"         \
    + "|" + "small"        \
    + "|" + "bufif1"       \
    + "|" + "large"        \
    + "|" + "specify"      \
    + "|" + "case"         \
    + "|" + "macromodule"  \
    + "|" + "specparam"    \
    + "|" + "casex"        \
    + "|" + "medium"       \
    + "|" + "strong0"      \
    + "|" + "casez"        \
    + "|" + "module"       \
    + "|" + "strong1"      \
    + "|" + "cmos"         \
    + "|" + "nand"         \
    + "|" + "supply0"      \
    + "|" + "deassign"     \
    + "|" + "negedge"      \
    + "|" + "supply1"      \
    + "|" + "default"      \
    + "|" + "nmos"         \
    + "|" + "table"        \
    + "|" + "defparam"     \
    + "|" + "nor"          \
    + "|" + "task"         \
    + "|" + "disable"      \
    + "|" + "not"          \
    + "|" + "time"         \
    + "|" + "edge"         \
    + "|" + "notif0"       \
    + "|" + "tran"         \
    + "|" + "else"         \
    + "|" + "notif1"       \
    + "|" + "tranif0"      \
    + "|" + "end"          \
    + "|" + "or"           \
    + "|" + "tranif1"      \
    + "|" + "endcase"      \
    + "|" + "output"       \
    + "|" + "tri"          \
    + "|" + "endmodule"    \
    + "|" + "parameter"    \
    + "|" + "tri0"         \
    + "|" + "endfunction"  \
    + "|" + "pmos"         \
    + "|" + "tri1"         \
    + "|" + "endprimitive" \
    + "|" + "posedge"      \
    + "|" + "triand"       \
    + "|" + "endspecify"   \
    + "|" + "primitive"    \
    + "|" + "trior"        \
    + "|" + "endtable"     \
    + "|" + "pull0"        \
    + "|" + "trireg"       \
    + "|" + "endtask"      \
    + "|" + "pull1"        \
    + "|" + "vectored"     \
    + "|" + "event"        \
    + "|" + "pullup"       \
    + "|" + "wait"         \
    + "|" + "for"          \
    + "|" + "pulldown"     \
    + "|" + "wand"         \
    + "|" + "force"        \
    + "|" + "rcmos"        \
    + "|" + "weak0"        \
    + "|" + "forever"      \
    + "|" + "real"         \
    + "|" + "weak1"        \
    + "|" + "fork"         \
    + "|" + "realtime"     \
    + "|" + "while"        \
    + "|" + "function"     \
    + "|" + "reg"          \
    + "|" + "wire"         \
    + "|" + "highz0"       \
    + "|" + "release"      \
    + "|" + "wor"          \
    + "|" + "highz1"       \
    + "|" + "repeat"       \
    + "|" + "xnor"         \
    + "|" + "if"           \
    + "|" + "rnmos"        \
    + "|" + "xor"


class LineType(Enum):
    COMMENT = 0
    INCLUDE = 1
    ASSIGN = 2
    DECL = 3
    LAST = 4


class AssignPasses(Enum):
    SYMBOL_TO_EQUAL = 0
    LAST = 1


class DeclPasses(Enum):                # logic [x:y] something = value;
    # [x:y]>>__<<something OR logic>>___<<something
    FIRST_SPACE = 0
    BRACKET_OR_KEYWORD_TO_SYMBOL = 1
    SYMBOL_TO_EQUAL = 2     # something>>___<<=
    LAST = 3


class CommentPasses(Enum):
    FIRST_SPACE = 0
    LAST = 1


class IncludePasses(Enum):
    FIRST_SPACE = 0
    LAST = 1


class LineGroup:
    def __init__(self, number_of_passes):
        self.number_of_passes = number_of_passes
        self.line_objects = []

    def add(self, line):
        self.line_objects.append(line)
        line.group = self

    def update_spaces(self):
        pass

    def format(self):
        for i in range(self.number_of_passes):
            for line in self.line_objects:
                line.format(pass_num = i)
            self.update_spaces(i)

    def idx_of_furthest_matching_regex_in_group(self, regex):
        res = -1
        for line in self.line_objects:
            idx = re.search(regex, line.text)
            if(idx == None):
                continue
            if(idx.start() > res):
                res = idx.start()
        return res

    def print_lines(self):
        for line in self.line_objects:
          print(line.text)


class EmptyGroup(LineGroup):
    def __init__(self):
        super(EmptyGroup, self).__init__(number_of_passes = 0)

class CommentGroup(LineGroup):
    def __init__(self):
        super(CommentGroup, self).__init__(number_of_passes = CommentPasses.LAST.value)
        self.spaces = [0 for _ in range(CommentPasses.LAST.value)]


class IncludeGroup(LineGroup):
    def __init__(self):
        super(IncludeGroup, self).__init__(number_of_passes = IncludePasses.LAST.value)
        self.spaces = [0 for _ in range(IncludePasses.LAST.value)]


class AssignGroup(LineGroup):
    def __init__(self):
        super(AssignGroup, self).__init__(number_of_passes = AssignPasses.LAST.value)
        self.spaces = [0 for _ in range(AssignPasses.LAST.value)]


class DeclGroup(LineGroup):
    def __init__(self):
        super(DeclGroup, self).__init__(number_of_passes = DeclPasses.LAST.value)
        self.spaces = [0 for _ in range(DeclPasses.LAST.value)]
        self.has_width_specifier = False

    def update_spaces(self):
        self.spaces[DeclPasses.BRACKET_OR_KEYWORD_TO_SYMBOL.value] = \
            max(self.idx_of_furthest_matching_regex_in_group("\][\s]+(\w)"),
                self.idx_of_furthest_matching_regex_in_group(KEYWORDS + "[\s]+(\w)"))  # TODO: Suboptimal
        self.spaces[DeclPasses.SYMBOL_TO_EQUAL.value] = self.idx_of_furthest_matching_regex_in_group(
            "\w[\s]+(=)")

class Line:
    def __init__(self, text, line_number):
        self.text = text
        self.line_number = line_number
        self.group = LineGroup(0)

    def get_pass_regexp(self, pass_num):
        return ["", ""]

    def format(self, pass_num):
        s1, s2 = self.get_pass_regexp(pass_num)
        self.text = re.sub(s1, s2, self.text)


class Comment(Line):
    def __init__(self, text, line_number):
        super(Comment, self).__init__(text, line_number)
        self.spaces = [0 for _ in range(CommentPasses.LAST.value)]

    def get_pass_regexp(self, pass_num):
        if(pass_num == 0):
            return ["include[\s]+\"", "include \""]


class Empty(Line):
    def __init__(self, text, line_number):
        super(Empty, self).__init__(text, line_number)


class Include(Line):
    def __init__(self, text, line_number):
        super(Include, self).__init__(text, line_number)
        self.spaces = [0 for _ in range(IncludePasses.LAST.value)]

    def get_pass_regexp(self, pass_num):
        if(pass_num == 0):
            return ["include[\s]+\"", "include \""]


class Assign(Line):
    def __init__(self, text, line_number):
        super(Assign, self).__init__(text, line_number)
        self.spaces = [0 for _ in range(AssignPasses.LAST.value)]

    def get_pass_regexp(self, pass_num):
        if(pass_num == 0):
            return ["assign[\s]+", "assign "]
        if(pass_num == 1):
            return ["[\s]+=[\s]+", self.group.spaces[AssignPasses.SYMBOL_TO_EQUAL.value]*" " + "= "]


class Decl(Line):
    def __init__(self, text, line_number, keyword_str):
        super(Decl, self).__init__(text, line_number)
        self.keyword_str = keyword_str
        self.spaces = [0 for _ in range(DeclPasses.LAST.value)]
        if(bool(re.search("\[", self.text))):
            self.has_width_specifier = True
        else:
            self.has_width_specifier = False

    def get_pass_regexp(self, pass_num):
        if(pass_num == 0):
            return [self.keyword_str + "[\s]+", self.keyword_str + " "]
        if(pass_num == 1):
            if (self.has_width_specifier):
                return ["(\][\s]+)\w", "]" + self.group.spaces[DeclPasses.BRACKET_OR_KEYWORD_TO_SYMBOL.value] * " "]
            return [KEYWORDS + "[\s]+\w", "]" + self.group.spaces[DeclPasses.BRACKET_OR_KEYWORD_TO_SYMBOL.value] * " "]
        if(pass_num == 2):
            return ["\w([\s]+=)", "]" + self.group.spaces[DeclPasses.SYMBOL_TO_EQUAL.value] * " " + "= "]


class Grouper:
    def __init__(self):
        self.groups = []
        self.current_type = None

    def current_group(self):
        if(self.groups == []):
            return None
        return self.groups[-1]

    def add_to_group(self, line):
        self.current_group().add(line)

    def new_group(self, type_str):
        if(type_str == "<class '__main__.Assign'>"):
            self.groups.append(AssignGroup())
        if(type_str == "<class '__main__.Decl'>"):
            self.groups.append(DeclGroup())
        if(type_str == "<class '__main__.Comment'>"):
            self.groups.append(CommentGroup())
        if(type_str == "<class '__main__.Include'>"):
            self.groups.append(IncludeGroup())
        if(type_str == "<class '__main__.Empty'>"):
            self.groups.append(EmptyGroup())
        self.current_type = type_str

class Liner:
    def __init__(self, filename):
        self.fd_r = open(filename, "r")
        self.lines_list = self.fd_r.readlines()
        self.number_of_lines = len(self.lines_list)
        self.lines_object = []
        self.grouper = Grouper()

    # def edit_line(self, line):
    #     self.lines_list[line.line_number] = line.format()

    # def write_lines(self):
    #     print(self.lines_list)
    #     # self.fd_w.writelines(self.lines_list)
   
    def parse(self):
        for i in range(self.number_of_lines):
            line_text = self.lines_list[i]
            if(bool(re.search("include", line_text))):
                self.lines_object.append(Include(line_text, i))

            elif(bool(re.search("\/\/", line_text)) or \
                 bool(re.search("\/\*", line_text)) or \
                 bool(re.search("\*\/", line_text))):
                self.lines_object.append(Comment(line_text, i))

            elif(bool(re.search("assign", line_text))):
                self.lines_object.append(Assign(line_text, i))
               
            elif(bool(re.search("wire", line_text))):
                self.lines_object.append(Decl(line_text, i, "wire"))

            elif(bool(re.search("logic", line_text))):
                self.lines_object.append(Decl(line_text, i, "logic"))

            elif(bool(re.search("reg", line_text))):
                self.lines_object.append(Decl(line_text, i, "reg"))

            elif(bool(re.search("input", line_text))):
                self.lines_object.append(Decl(line_text, i, "input"))

            elif(bool(re.search("output", line_text))):
                self.lines_object.append(Decl(line_text, i, "output"))

            elif(bool(re.search("[\s]*\n", line_text))):
                self.lines_object.append(Empty(line_text, i))

    def group_and_format(self): 
        for line in self.lines_object:
            t = str(type(line))
            if(self.grouper.current_type == None):
                self.grouper.new_group(t)  
                self.grouper.add_to_group(line)
            else:
                if(t != self.grouper.current_type):
                    self.grouper.current_group().format()
                    self.grouper.new_group(t)  
                self.grouper.add_to_group(line)

    
def pre_proc(file_name, preproc_file_name):
    match_cmd   = "(?=[^;]*;[^;]*)((;)(?=))"
    replace_cmd = ";\n" 
    os.system("perl -p -e \"s/" + match_cmd + "/" +
              replace_cmd + "/g\" " + file_name + " > " + preproc_file_name)


if __name__ == "__main__":
    pre_proc(FILE, PREPROC_FILE)
    liner = Liner(PREPROC_FILE)
    liner.parse()
    liner.group_and_format()


# class Import(Line):
#     pass
# class Module(Line):
#     pass
# class Parameter(Line):
#     pass
# class LocalParameter(Line):
#     pass
# class IO(Line):
#     pass
# class Module(Line):
#     pass
# class ModuleInstParameter(Line):
#     pass
# class ModuleInstLocalParameter(Line):
#     pass
# class ModuleInstIO(Line):
#     pass
# class Decl(Line):
#     pass
# class Assign(Line):
#     pass
