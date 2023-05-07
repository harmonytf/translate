import pytest

from translate.storage import base, test_monolingual, vdf

#class TestVDFResourceUnit(test_monolingual.TestMonolingualUnit):
#    UnitClass = vdf.VDFUnit
#
#    def test_getlocations(self):
#        unit = self.UnitClass('')
#        unit.setid("SOME_KEY")
#        assert unit.getlocations() == ["SOME_KEY"]

class TestVDFFileLine:
    def test1(self):
        line = vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE" [$PS4]')
        assert line.cond == "$PS4"
        assert line.effectiveKey == "SOME_KEY[$PS4]"

    def test2(self):
        line = vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE" [!$PS4]')
        assert line.cond == "!$PS4"

    def test3(self):
        line = vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE" [$PS4]')
        line.set_key("SOME_OTHER_KEY")
        assert line.key == "SOME_OTHER_KEY"
        assert line.cond == "$PS4"
        assert line.effectiveKey == "SOME_OTHER_KEY[$PS4]"
        line.set_key("SOME_OTHER_KEY[$PS5]")
        assert line.key == "SOME_OTHER_KEY"
        assert line.cond == "$PS5"
        assert line.effectiveKey == "SOME_OTHER_KEY[$PS5]"

class TestVDFResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = vdf.VDFUnit

    def test1(self):
        unit = self.UnitClass(vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE"'))
        assert unit.getlocations() == ["SOME_KEY"]

    def test2(self):
        unit = self.UnitClass(vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE"'))
        unit.setid("SOME_OTHER_KEY")
        assert unit.getlocations() == ["SOME_OTHER_KEY"]
        assert unit.getvalue() == {"SOME_OTHER_KEY": "SOME_VALUE"}
    
    def test3(self):
        unit = self.UnitClass(vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE"'))
        unit.set_unitid(self.UnitClass.IdClass([("key", "SOME_OTHER_KEY")]))
        assert unit._id == "SOME_OTHER_KEY"
        assert str(unit._unitid) == "SOME_OTHER_KEY"
        assert unit.getlocations() == ["SOME_OTHER_KEY"]
        assert unit.getvalue() == {"SOME_OTHER_KEY": "SOME_VALUE"}
    
    def test3_cond(self):
        unit = self.UnitClass(vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE" [$PS4]'))
        unit.set_unitid(self.UnitClass.IdClass([("key", "SOME_OTHER_KEY"), ("index", "$PS5")]))
        assert unit._id == "SOME_OTHER_KEY[$PS5]"
        assert str(unit._unitid) == "SOME_OTHER_KEY[$PS5]"
        assert unit.getlocations() == ["SOME_OTHER_KEY[$PS5]"]
        assert unit.getvalue() == {"SOME_OTHER_KEY[$PS5]": "SOME_VALUE"}

    def test4(self):
        unit = self.UnitClass(vdf.VDFFileLine(' "SOME_KEY" "SOME_VALUE"//comment'))
        unit.target = "SOME_OTHER_VALUE"
        assert unit.getvalue() == {"SOME_KEY": "SOME_OTHER_VALUE"}
        assert unit.line.line == ' "SOME_KEY" "SOME_OTHER_VALUE"//comment'

    def test_empty_val_insertion(self):
        unit = self.UnitClass(vdf.VDFFileLine(' "EMPTY" ""'))
        unit.target = "SOME_OTHER_VALUE"
        assert unit.getvalue() == {"EMPTY": "SOME_OTHER_VALUE"}
        assert unit.line.line == ' "EMPTY" "SOME_OTHER_VALUE"'

    def test_key_and_val_change(self):
        line = vdf.VDFFileLine(' "OLD_KEY" "VALUE"')
        line.set_key("NEW_KEY______")
        line.set_value("NEW_VALUE")
        assert line.key == "NEW_KEY______"
        assert line.value == "NEW_VALUE"
        assert line.line == ' "NEW_KEY______" "NEW_VALUE"'

    def test_ending_escaped_backslash(self):
        unit = self.UnitClass(vdf.VDFFileLine(' "SOME_KEY" "SOME_VALUE\\\\"//comment'))
        assert unit.target == "SOME_VALUE\\"
        unit.target = "SOME_OTHER_VALUE\\"
        assert unit.getvalue() == {"SOME_KEY": "SOME_OTHER_VALUE\\"}
        assert unit.line.line == ' "SOME_KEY" "SOME_OTHER_VALUE\\\\"//comment'

    def test_ending_escaped_quote(self):
        unit = self.UnitClass(vdf.VDFFileLine(' "SOME_KEY" "SOME_VALUE\\""//comment'))
        assert unit.target == 'SOME_VALUE"'
        unit.target = 'SOME_OTHER_VALUE"'
        assert unit.getvalue() == {"SOME_KEY": "SOME_OTHER_VALUE\""}
        assert unit.line.line == ' "SOME_KEY" "SOME_OTHER_VALUE\\""//comment'

    def test_escaping_integrity(self):
        # check if reading and setting the same value will result in the same line
        #orig = r'"TEST_ESCAPES" "\"We test escapes\"\"\", trololo\\\",\ \\ \\\ \\\\, enter:\npost\\n-\\\nenter, tab:\tpost-\\taaa\\\taaa\b:)\""'
        orig = r'"TEST_ESCAPES" "\"We test escapes\"\"\", trololo\\\",\\ \\\\, enter:\npost\\n-\\\nenter, tab:\tpost-\\taaa\\\taaa\b:)\""'
        unit = self.UnitClass(vdf.VDFFileLine(orig))
        val = unit.target + ""
        unit.target = "TEMP_DIFFERENT"
        unit.target = val # set it back
        assert unit.target == val
        assert unit.line.line == orig

    def test_escaping1(self):
        unit = self.UnitClass(vdf.VDFFileLine(r' "SOME_KEY" "\"Refueling Raid\""//comment'))
        assert unit.getvalue() == {"SOME_KEY": r'"Refueling Raid"'}

    def test_escaping2(self):
        unit = self.UnitClass(vdf.VDFFileLine(r' "SOME_KEY" "\"SOME_\\nVALUE\""//comment'))
        assert unit.getvalue() == {"SOME_KEY": r'"SOME_\nVALUE"'}
        unit.target = r'"SOME_OTHER_\\nVALUE"'
        assert unit.getvalue() == {"SOME_KEY": r'"SOME_OTHER_\\nVALUE"'}
        assert unit.line.line == r' "SOME_KEY" "\"SOME_OTHER_\\\\nVALUE\""//comment'
        unit.target = '"SOME_\tOTHER_\\\nVALUE"'
        assert unit.getvalue() == {"SOME_KEY": '"SOME_\tOTHER_\\\nVALUE"'}
        assert unit.line.line == ' "SOME_KEY" "\\"SOME_\\tOTHER_\\\\\\nVALUE\\""//comment'

    def test_escaping3(self):
        unit = self.UnitClass(vdf.VDFFileLine(r'"TEST_ESCAPES" "\"We test escapes\"\"\", trololo\\\", enter:\npost-enter, tab:\tpost-\\ta\b:)\""'))
        assert unit.target == r'"We test escapes""", trololo\", enter:' + "\npost-enter, tab:\tpost-" + r'\ta' + "\b" + r':)"'
        unit.target = unit.target[0:6] + "<NEW>" + unit.target[6:]
        assert unit.line.line == r'"TEST_ESCAPES" "\"We te<NEW>st escapes\"\"\", trololo\\\", enter:\npost-enter, tab:\tpost-\\ta\b:)\""'

    def test_no_unnecessary_escape(self):
        unit = self.UnitClass(vdf.VDFFileLine(r' "SOME_KEY" ""'))
        unit.target = r'\"' + r"'?ntvbrfa"
        assert unit.line.line == r' "SOME_KEY" "\\\"' + r"'?ntvbrfa" + r'"'

    def test_cond(self):
        unit = self.UnitClass(vdf.VDFFileLine('"SOME_KEY" "SOME_VALUE" [$PS4]'))
        assert unit.getlocations() == ["SOME_KEY[$PS4]"]

class TestVDFResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = vdf.VDFFile
    StoreClassUTF16 = vdf.VDFFileUTF16

    def test_serialize(self):
        store = self.StoreClass()
        input = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		"SOME_KEY"  "SOME_VALUE"
	}
}
"""
        store.parse(input)
        assert bytes(store) == bytes(input, "utf-8")
        assert len(store._original._lines) == 8

    def test_serialize_with_changed_value_by_unit(self):
        store = self.StoreClass()
        input = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"SOME_KEY"    "SOME_VALUE" //comment
	}
}
"""
        output_expected = bytes(""""lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"SOME_KEY"    "SOME_OTHER_VALUE" //comment
	}
}
""", "utf-8")

        store.parse(input)
        assert store._original["SOME_KEY"] == "SOME_VALUE"
        store.units[0].target = "SOME_OTHER_VALUE"
        assert store._original["SOME_KEY"] == "SOME_OTHER_VALUE"
        assert bytes(store) == output_expected

    def test_remove(self):
        store = self.StoreClass()
        input = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"BEFORE_KEY" "before value"
		"SOME_KEY"    "SOME_VALUE" //to be removed
		"AFTER_KEY" "after value"

		"AFTER_KEY2" "after value"
	}
}
"""
        output_expected = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"BEFORE_KEY" "before value"
		"AFTER_KEY" "after value"

		"AFTER_KEY2" "after value"
	}
}
"""

        store.parse(input)
        assert len(store.units) == 4
        assert bytes(store).decode() == input
        store.removeunit(store.units[1])
        #assert bytes(store) == bytes(output_expected, "utf-8")
        assert bytes(store).decode() == output_expected

    def test_empty(self):
        store = self.StoreClass()
        store.parse(vdf.vdfTranslationBase)
        assert bytes(store).decode() == vdf.vdfTranslationBase

    def test_create_base(self):
        store = self.StoreClass()
        assert bytes(store).decode() == vdf.vdfTranslationBase

    def test_create(self):
        store = self.StoreClass()
        unit1 = store.addsourceunit("TEST_STRING")
        unit1.target = "TEST_VALUE"
        assert len(store.units) == 1
        output_expected = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		"TEST_STRING" "TEST_VALUE"
	}
}
"""
        assert bytes(store).decode() == output_expected

        unit2 = store.addsourceunit("TEST_STRING2")
        unit2.target = "TEST_VALUE2"
        assert len(store.units) == 2
        output_expected = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		"TEST_STRING" "TEST_VALUE"
		"TEST_STRING2" "TEST_VALUE2"
	}
}
"""
        assert bytes(store).decode() == output_expected

    def test_parse_utf16(self):
        store = self.StoreClassUTF16()
        input = bytes.fromhex("FFFE22006C0061006E00670022000D000A007B000D000A00090022004C0061006E006700750061006700650022002000220065006E0067006C0069007300680022000D000A000900220054006F006B0065006E00730022000D000A0009007B000D000A000900090022004B00450059003100220020002200560041004C00310022000D000A000900090022004B00450059003200220020002200560041004C00320022000D000A0009007D000D000A007D00")
        store.parse(input)
        assert len(store.units) == 2
        assert bytes(store) == input

    def test_with_conditional(self):
        store = self.StoreClass()
        input = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"BEFORE_KEY" "before value"
		"SOME_KEY"    "SOME_VALUE" //comment
		"AFTER_KEY" "after value" [$PS4]

		"AFTER_KEY2" "after value"
	}
}
"""

        store.parse(input)
        assert len(store.units) == 4
        assert bytes(store).decode() == input
        #store.removeunit(store.units[1])
        #assert bytes(store) == bytes(output_expected, "utf-8")
        #assert bytes(store).decode() == output_expected