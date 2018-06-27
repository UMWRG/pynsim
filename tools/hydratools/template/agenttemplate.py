# -*- coding: utf-8 -*-

from pynsim import {{agent_type}}
{% for resource in resources %}

class {{resource.name.replace(' ', '')}}({{agent_type}}):
    type = "{{resource.name}}"
    _properties = { {%- for attr in resource.typeattrs -%}
                   '{{attr_lookup[attr.attr_id].name}}': 0,
                   {% endfor -%}
                   }

    def setup(self, t):
        pass
{% endfor %}
