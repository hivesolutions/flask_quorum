#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Flask Quorum
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Flask Quorum.
#
# Hive Flask Quorum is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Flask Quorum is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Flask Quorum. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import quorum

from . import mock

class ModelTest(quorum.TestCase):

    def setUp(self):
        try:
            quorum.load(
                name = __name__,
                mongo_database = "test",
                models = mock
            )
        except:
            self.skip()

    def tearDown(self):
        try:
            adapter = quorum.get_adapter()
            adapter.drop_db()
        except: pass
        finally: quorum.unload()

    @quorum.secured
    def test_basic(self):
        person = mock.Person()
        person.name = "Name"

        self.assertEqual(person.name, "Name")
        self.assertEqual(person["name"], "Name")
        self.assertEqual(len(person), 1)

        person["age"] = 20

        self.assertEqual(person.age, 20)
        self.assertEqual(person["age"], 20)
        self.assertEqual(len(person), 2)

        self.assertEqual("age" in person, True)
        self.assertEqual("boss" in person, False)
        self.assertEqual(bool(person), True)

        del person["name"]

        self.assertRaises(AttributeError, lambda: person.name)
        self.assertRaises(KeyError, lambda: person["name"])

        del person.age

        self.assertRaises(AttributeError, lambda: person.age)
        self.assertRaises(KeyError, lambda: person["age"])

        self.assertEqual(bool(person), False)

    @quorum.secured
    def test_find(self):
        result = mock.Person.find(age = 1)
        self.assertEqual(len(result), 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.find(age = 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age, 1)

    @quorum.secured
    def test_count(self):
        result = mock.Person.count()
        self.assertEqual(result, 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.count()
        self.assertEqual(result, 1)

    @quorum.secured
    def test_delete(self):
        result = mock.Person.count()
        self.assertEqual(result, 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.count()
        self.assertEqual(result, 1)

        person.delete()

        result = mock.Person.count()
        self.assertEqual(result, 0)

    @quorum.secured
    def test_validation(self):
        person = mock.Person()

        self.assertRaises(quorum.ValidationError, person.save)

        person = mock.Person()
        person.name = "Name"
        person.save()

        person = mock.Person()
        person.name = "Name"

        self.assertRaises(quorum.ValidationError, person.save)

    @quorum.secured
    def test_map(self):
        person = mock.Person()
        person.name = "Name"

        self.assertEqual(person.name, "Name")

        person.save()

        self.assertEqual(person.identifier, 1)
        self.assertEqual(person.identifier_safe, 1)
        self.assertEqual(person.name, "Name")

        person_m = person.map()

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["identifier_safe"], 1)
        self.assertEqual(person_m["name"], "Name")

        person.age = 20
        person.hidden = "Hidden"

        self.assertEqual(person.age, 20)
        self.assertEqual(person.hidden, "Hidden")

        person_m = person.map(all = True)

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["identifier_safe"], 1)
        self.assertEqual(person_m["name"], "Name")
        self.assertEqual(person_m["age"], 20)
        self.assertEqual(person_m["hidden"], "Hidden")

        cat = mock.Cat()
        cat.name = "NameCat"

        self.assertEqual(cat.name, "NameCat")

        cat.save()

        self.assertEqual(cat.identifier, 1)

        person.cats = [cat]
        person.save()

        person_m = person.map(resolve = True, all = True)

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(isinstance(person_m["cats"], list), True)
        self.assertEqual(isinstance(person_m["cats"][0], dict), True)
        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["identifier_safe"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person_m = person.map(all = True)

        self.assertEqual(person_m["cats"][0], 1)

        person_m = person.map(resolve = True, all = True)

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(isinstance(person_m["cats"], list), True)
        self.assertEqual(isinstance(person_m["cats"][0], dict), True)
        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["identifier_safe"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")

    @quorum.secured
    def test_references(self):
        person = mock.Person()
        person.name = "Name"

        cat = mock.Cat()
        cat.name = "NameCat"
        cat.save()

        person.cats = [cat]
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person.cats = mock.Person.cats["type"]([cat])
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person = mock.Person.get(identifier = 1, map = True)

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(isinstance(person["cats"][0], int), True)
        self.assertEqual(len(person["cats"]), 1)

        person = mock.Person.get(
            identifier = 1,
            map = True,
            eager = ("cats",)
        )

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(isinstance(person["cats"][0], dict), True)

        person = mock.Person.get(identifier = 1)

        person.cats = []
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(len(person.cats), 0)

        person = mock.Person.get(map = True, eager = ("cats",))

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(len(person["cats"]), 0)

        father = mock.Person()
        father.name = "father"
        father.save()

        person = mock.Person.get(identifier = 1)
        person.father = father
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(isinstance(person.father, quorum.Reference), True)
        self.assertEqual(person.father.name, "father")

        person = mock.Person.get(identifier = 1)

        person.father.name = "father_changed"
        person.father.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.father.name, "father_changed")
