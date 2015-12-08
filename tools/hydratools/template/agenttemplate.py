# -*- coding: utf-8 -*-

from pynsim import {{agent_type}}
{% for resource in resources %}

class {{resource.class_name}}({{agent_type}}):
    type = "{{resource.type_name}}"
    _properties = { {%- for attr in resource.attributes -%}
                   '{{attr.name}}': {{attr.value}},
                   {% endfor -%}
                   }

    def setup(self, t):
        pass
{% endfor %}
