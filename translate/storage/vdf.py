#import uuid
import re
from io import BufferedWriter

#from ruamel.yaml import YAML, YAMLError
#from ruamel.yaml.comments import CommentedMap, TaggedScalar

from translate.storage import base

class VDFUnitId(base.UnitId):
    KEY_SEPARATOR = "->"

    def __str__(self):
        result = super().__str__()
        # Strip leading ->
        if result.startswith(self.KEY_SEPARATOR):
            return result[len(self.KEY_SEPARATOR) :]
        return result

    #@classmethod
    #def from_string(cls, text):
    ##    if text.startswith(cls.KEY_SEPARATOR):
    #        key = text[len(cls.KEY_SEPARATOR) :]
    #    else:
    #        key = text
    #    #return cls([("key", key)])
    #    return cls.from_string(key)

    #def __str__(self):
    #    result = super().__str__()
    #    # Strip conditionals
    #    if "[" in result:
    #        return result[0 : result.find("[")]
    #    return result

class VDFUnit(base.DictUnit):
    """A VDF entry"""

    IdClass = VDFUnitId
    #IdClass = base.UnitId
    DefaultDict = dict

    def __init__(self, source=None, **kwargs):

        if isinstance(source, VDFFileLine):# and source.valid:
            line = source
            self.line = line
            self._id = line.key
            #if line.cond is not None:
            #    self.set_unitid((self.IdClass([("key", line.key), ("key", line.cond)])))
            #else:
            #    self.set_unitid(self.IdClass([("key", line.key)]))
            #self._id = str(self._unitid)
            super().__init__(line.key)
            self._target = line.value
            if line.cond is not None:
                self.set_unitid((self.IdClass([("key", line.key), ("key", line.cond)])))
            else:
                self.set_unitid(self.IdClass([("key", line.key)]))
        else:
            #self.line = VDFFileLine('		"' + source + '" ""')
            self.line = VDFFileLine(vdfPlaceholderLine)
            self.line.set_key(source)
            #self.set_unitid(self.IdClass([("key", source)]))
            self._id = source
            super().__init__(source)
            self._target = ""
            if self.line.cond is not None:
                self.set_unitid((self.IdClass([("key", self.line.key), ("key", self.line.cond)])))
            else:
                self.set_unitid(self.IdClass([("key", self.line.key)]))

        # Ensure we have ID (for serialization)
        #if source:
        #    self.source = source
        #    self._id = hex(hash(source))
        #else:
        #    self._id = str(uuid.uuid4())
        #super().__init__(source)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        """Set the source string to the given value."""
        #self._rich_source = None
        self._source = str(source)
        self.setid(source)
        self.line.set_key(str(source))

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        """Set the target string to the given value."""
        #self._rich_target = None
        self._target = str(target)
        self.line.set_value(str(target)) # doesn't seem to always work how it should...

    def setid(self, value):
        self._id = value
        #self._unitid = None
        self._unitid = self.IdClass.from_string(value)

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def convert_target(self):
        return self.target

    def storevalues(self, output):
        self.storevalue(output, self.convert_target())

vdfTranslationBase = """"lang"
{
	"Language" "english"
	"Tokens"
	{
	}
}
"""

vdfPlaceholderLine = '		"PLACEHOLDER" ""\n' # \n? TODO: check with random line end of file what's the line ending (this will only fallback to placeholder in rare cases of inserting new unit)

# Regex to fix the below
# titanfall2/r1/fr: skipping update due to parse error: String contains control char: '%$rui\hud\gametype_icons\bounty_hunt\bh_titan% New Bounty Incoming'
_rui_cleanup_regex = re.compile(r'(%\$(?:rui|vgui)[A-Za-z0-9_\\]*)(\\)([A-Za-z0-9_\\/]*?%)')

# TODO fix:
# ^ we might need to add unescaped version of VDF format entries...
def unescape(string: str) -> str:
    #return str(string).replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
    string = str(string)

    # Fix Titanfall 2 edge case (single key using unescaped forward slashes instead of backward)
    while _rui_cleanup_regex.match(string):
        string = re.sub(_rui_cleanup_regex, "\\1/\\3", string)

    # only unescape if the backslash before doesn't have another backslash before (ie. isn't escaped itself like: \\test <- a tabulator should not be inserted there)
    # however we keep the \\ intact without escaping in case there are other \<letter> escapes that we aren't handling which we'd break otherwise
    # string = re.sub(r'([^\\]|^|)\\([\\])', r'\1\2', string)
    # string = re.sub(r'([^\\]|^|)\\(["\'\?])', r'\1\2', string)
    # string = re.sub(r'([^\\]|^|)\\([n])', '\\1\n', string)
    # string = re.sub(r'([^\\]|^|)\\([t])', '\\1\t', string)
    # string = re.sub(r'([^\\]|^|)\\([v])', '\\1\v', string)
    # string = re.sub(r'([^\\]|^|)\\([b])', '\\1\b', string)
    # string = re.sub(r'([^\\]|^|)\\([r])', '\\1\r', string)
    # string = re.sub(r'([^\\]|^|)\\([f])', '\\1\f', string)
    # string = re.sub(r'([^\\]|^|)\\([a])', '\\1\a', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(["\'\?])', '\\1\\2', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(n)', '\\1\n', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(t)', '\\1\t', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(v)', '\\1\v', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(b)', '\\1\b', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(r)', '\\1\r', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(f)', '\\1\f', string)
    string = re.sub(r'(?<!\\)(\\\\)*\\(a)', '\\1\a', string)
    string = re.sub(r'\\\\', r'\\', string)
    # fixup
    return string
def escape(string: str) -> str:
    return (str(string)
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\t', '\\t')
        #.replace("'", "\\'") # no need to escape
        #.replace('?', '\\?') # no need to escape
        .replace('\v', '\\v')
        .replace('\b', '\\b')
        .replace('\r', '\\r')
        .replace('\f', '\\f')
        .replace('\a', '\\a')
    )

#_vdf_regex = re.compile(r'^\s*\"(?P<key>.+?)(?:(?<!\\)\")\s+\"(?P<val>.*?)(?:(?<!\\)\")\s*(?P<cond>\[[^\]\/]*\])?\s*(?:\/+.*)?$', re.UNICODE)
#_vdf_regex = re.compile(r'^\s*\"(?P<key>.+?)(?:(?<!\\)\")\s+\"(?P<val>.*?)(?:(?<!\\)\")\s*(?:\[(?P<cond>[^\]\/]*)\])?\s*(?:\/+.*)?$', re.UNICODE)
_vdf_regex = re.compile(r'^\s*\"(?P<key>.+?(?<!\\)(?:\\\\)*)(?:\")\s+\"(?P<val>.*?(?<!\\)(?:\\\\)*)(?:\")(?:\s*\[(?P<cond>[^\]\/]*)\])?(?P<comment>\s*\/+[^\r\n]*)?\s*$', re.UNICODE)

class VDFFileLine(object):
    def __init__(self, line):
        self.line = line
        self.refresh_regex()

    def refresh_regex(self):
        matched = _vdf_regex.match(self.line)
        self.valid = matched is not None

        if self.valid:
            self.key = unescape(matched.group('key'))
            self.value = unescape(matched.group('val'))
            self.posKey = matched.span('key')
            self.posValue = matched.span('val')
            #self.effectiveKey = self.key
            #if matched.group('cond') is not None:
            #    self.effectiveKey += matched.group('cond')
            self.cond: str | None = matched.group('cond')
            self.comment: str | None = matched.group('comment')
            self.posComment: tuple[int, int] | None = matched.span('comment')

    def __str__(self) -> str:
        return self.line

    def set_value(self, new_value):
        new_value_escaped = escape(new_value)
        self.line = self.line[0 : self.posValue[0]] + new_value_escaped + self.line[self.posValue[1] : ]
        self.value = new_value
        delta = (self.posValue[0] + len(new_value_escaped)) - self.posValue[1]
        self.posValue = ( self.posValue[0], self.posValue[0] + len(new_value_escaped) )
        if self.comment:
            self.posComment = ( self.posComment[0] + delta, self.posComment[1] + delta )
        #self.refresh_regex()

    def set_key(self, new_key):
        new_key_escaped = escape(new_key)
        self.line = self.line[0 : self.posKey[0]] + new_key_escaped + self.line[self.posKey[1] : ]
        self.key = new_key
        delta = (self.posKey[0] + len(new_key_escaped)) - self.posKey[1]
        self.posKey = ( self.posKey[0], self.posKey[0] + len(new_key_escaped) )
        self.posValue = ( self.posValue[0] + delta, self.posValue[1] + delta )
        if self.comment:
            self.posComment = ( self.posComment[0] + delta, self.posComment[1] + delta )
        #self.refresh_regex() # to update value pos

    def remove_comment(self):
        if self.comment:
            self.line = self.line[0 : self.posComment[0]] + self.line[self.posComment[1] : ]
            self.comment = None


class VDFFileWrapper(object):
    def __init__(self, contents=None):
        self._raw = contents if contents is not None and contents != "" else vdfTranslationBase
        self._lines = []
        self._linesMap = {}
        #for line in self._raw:
        for line in self._raw.splitlines(keepends=True):
            line = VDFFileLine(line)
            self._addline_bottom(line)

    def _addline_bottom(self, line):
        self._lines.append(line)
        if line.valid:
            self._linesMap[line.key] = line

    def _addline_sane(self, line):
        valid_lines = list(filter(lambda line: line.valid, self._lines))
        opening_lines = list(filter(lambda line: not line.valid and "{" in line.line, self._lines))
        # `len(valid_lines) > 1` so it skips the first "Language" kv
        insert_at = (self._lines.index(valid_lines[-1])+1) if len(valid_lines) > 1 else ((self._lines.index(opening_lines[-1])+1) if len(opening_lines) else len(self._lines))
        self._lines.insert(insert_at, line)
        if line.valid:
            self._linesMap[line.key] = line
    
    def __getitem__(self, key: str):
        if key in self._linesMap:
            return self._linesMap[key].value

        raise KeyError

    def __setitem__(self, key: str, value: str):
        if key in self._linesMap:
            self._linesMap[key].set_value(value)
        else:
            valid_lines = list(filter(lambda line: line.valid, self._lines))
            #last_line_text = valid_lines[-1].line if len(valid_lines) else vdfPlaceholderLine
            last_line_text =  vdfPlaceholderLine
            if len(valid_lines) > 1: # `len(valid_lines) > 1` so it skips the first "Language" kv
                last_line_text = valid_lines[-1].line
            new_line = VDFFileLine(last_line_text)
            assert new_line.valid
            new_line.set_key(key)
            new_line.set_value(value)
            new_line.remove_comment()
            assert new_line.valid
            self._addline_sane(new_line)

    def __delitem__(self, key: str) -> None:
        self._lines = [item for item in self._lines if not item.valid or item.key != key]
        if key in self._linesMap:
            del self._linesMap[key]

class VDFFile(base.DictStore):
    """A Valve VDF file"""

    UnitClass = VDFUnit
    Encoding = "UTF-8"

    def __init__(self, inputfile=None, **kwargs):
        """construct a Valve VDF file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self._original = VDFFileWrapper()
        if inputfile is not None:
            self.parse(inputfile)

    def serialize(self, out: BufferedWriter):
        # Always start with valid root even if original file was empty
        if self._original is None:
            self._original = VDFFileWrapper()

        #units = self.preprocess(self._original)
        #self.serialize_units(units)
        self.serialize_units(self._original)
        #YAML().dump(self._original, out)
        #out = "\n".join(self._original._lines)
        for line in self._original._lines:
            out.write(bytes(line.line, self.Encoding))

    @staticmethod
    def preprocess(data):
        """Preprocess hook for child formats"""
        return data

    def parse(self, input):
        """parse the given file or file source string"""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            src = input.read()
            input.close()
            input = src
        
        if isinstance(input, bytes):
            input = input.decode(self.Encoding)
            # First let's try the default codec, which is the normally supported by Valve games
            ##try:
            ##    input = input.decode('utf-16') # UTF-16-LE
            ##    self.encoding = 'utf-16-le'
            ##except:
            ##    #result = chardet.detect(rawdata)
            ##    #self.codec = result['encoding']
            ##    #if self.codec.lower() == 'ascii': # If it's ascii, convert automatically to UTF-8, as UTF-8 is completely valid for ASCII
            ##    #    self.codec = 'utf-8'
            ##    #self.content = rawdata.decode(self.codec)
            ##    input = input.decode("utf-8")
            ##    self.encoding = 'utf-8'

        self._original = VDFFileWrapper(input)

        #for k, data in self._flatten(self._original):
        #    unit = self.UnitClass(data)
        #    unit.set_unitid(k)
        #    self.addunit(unit)

        #for line_number, line in enumerate(self._original._lines, 1):
        for line in self._original._lines:
            if isinstance(line, VDFFileLine) and line.valid and not (len(self.units) == 0 and line.key == "Language"):
                unit = self.UnitClass(line)
                #unit.set_unitid([("key", line.effectiveKey)])
                self.addunit(unit)

    def removeunit(self, unit):
        if self._original is not None:
            unit.storevalue(self._original, "", unset=True)
        super().removeunit(unit)

    def addunit(self, unit):
        if self._original is not None:
            unit.storevalues(self._original) # it will recreate the VDFFileLine though...
        super().addunit(unit)

    def addsourceunit(self, source):
        unit = self.UnitClass(source)
        if self._original is not None:
            self._original[source] = ""
        super().addunit(unit)
        return unit

class VDFFileUTF16(VDFFile):
    Encoding = "UTF-16-LE"
