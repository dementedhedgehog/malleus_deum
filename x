



	<bold>Crit Class:</bold> {{ check.crit_class }}<br/>
	{%- if check.any_success -%}
	<bold>Any-Success:</bold> {{ check.any_success }}<br/>
	{%- endif -%}
	{% if check.critsuccess %}
	<bold>Critical Success:</bold> {{ check.critsuccess }}<br/>
	{%- endif %}
	{%- if check.righteoussuccess -%}
	<bold>Righteous Success:</bold> {{ check.righteoussuccess }}<br/>
	{%- endif %}
	{% if check.success -%}
	<bold>Success:</bold> {{ check.success }}<br/>
	{%- endif -%}
	{% if check.any_fail -%}
	<bold>Any-Fail:</bold> {{ check.any_fail }}<br/>
	{%- endif %}
	{%- if check.fail -%}
	<bold>Fail:</bold> {{ check.fail }}<br/>
	{%- endif %}
	{%- if check.grimfail -%}
	<bold>Grim Fail:</bold> {{ check.grimfail }}<br/>
	{%- endif %}
	{%- if check.critfail -%}
	<bold>Critical Fail:</bold> {{ check.critfail }}<br/>
	{%- endif -%}
	{% if check.blessed -%}
	<bold>Blessed:</bold> {{ check.boon }}<br/>
	{%- endif %}
	{% if check.boon -%}
	<bold>Lucky:</bold> {{ check.lucky }}<br/>
	{%- endif %}
	<!-- {% if check.indifferent -%} -->
	<!-- <bold>Indifferent:</bold> {{ check.indifferent }}<br/> -->
	<!-- {%- endif %} -->
	{% if check.damned -%}
	<bold>Damned:</bold> {{ check.damned }}<br/>
	{%- endif %}
	{% if check.cursed -%}
	<bold>Cused:</bold> {{ check.cursed }}<br/>
	{%- endif %}            


