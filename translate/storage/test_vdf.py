import pytest

from translate.storage import base, test_monolingual, vdf

#class TestVDFResourceUnit(test_monolingual.TestMonolingualUnit):
#    UnitClass = vdf.VDFUnit
#
#    def test_getlocations(self):
#        unit = self.UnitClass('')
#        unit.setid("SOME_KEY")
#        assert unit.getlocations() == ["SOME_KEY"]

class TestVDFResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = vdf.VDFUnit
    print("aaaa")

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

    def test4(self):
        unit = self.UnitClass(vdf.VDFFileLine(' "SOME_KEY" "SOME_VALUE"//comment'))
        unit.target = "SOME_OTHER_VALUE"
        assert unit.getvalue() == {"SOME_KEY": "SOME_OTHER_VALUE"}
        assert unit.line.line == ' "SOME_KEY" "SOME_OTHER_VALUE"//comment'

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

    #def test_empty(self):
    #    store = self.StoreClass()
    #    store.parse("{}")
    #    assert bytes(store) == b"{}\n"

    def test_remove(self):
        store = self.StoreClass()
        input = """"lang"
{
	"Language" "english"
	"Tokens"
	{
		//comment
		"BEFORE_KEY" "before value"
		"SOME_KEY"    "SOME_VALUE" //comment
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