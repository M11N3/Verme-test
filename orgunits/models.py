"""
Copyright 2020 ООО «Верме»
"""

from django.db import models
from django.db.models.expressions import RawSQL


class OrganizationQuerySet(models.QuerySet):
    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """
        query = "WITH RECURSIVE tree(id, name, code, parent_id)               \
                AS (SELECT id, name, code, parent_id                          \
                    FROM orgunits_organization                                \
                    WHERE id = %s                                             \
                UNION ALL                                                     \
                SELECT orgunits_organization.id,                              \
                    orgunits_organization.name,                               \
                    orgunits_organization.code,                               \
                    orgunits_organization.parent_id                           \
                FROM orgunits_organization                                    \
                INNER JOIN tree ON tree.id = orgunits_organization.parent_id) \
                SELECT id FROM tree                                           \
                "
        return self.filter(id__in=RawSQL(query, [root_org_id]))

    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """
        query = "WITH RECURSIVE tree(id, name, code, parent_id)               \
                AS (SELECT id, name, code, parent_id                          \
                    FROM orgunits_organization                                \
                    WHERE id = %s                                             \
                UNION ALL                                                     \
                    SELECT orgunits_organization.id,                          \
                           orgunits_organization.name,                        \
                           orgunits_organization.code,                        \
                           orgunits_organization.parent_id                    \
                FROM orgunits_organization                                    \
                INNER JOIN tree ON tree.parent_id = orgunits_organization.id) \
                SELECT id FROM tree                                           \
                "
        return self.filter(id__in=RawSQL(query, [child_org_id]))


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организация"
        verbose_name = "Организации"

    def __str__(self):
        return self.name

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """
        return Organization.objects.tree_upwards(self.id).exclude(id=self.id)

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """
        return Organization.objects.tree_downwards(self.id).exclude(id=self.id)
