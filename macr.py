{% macro build_ability(ability) %}
<subsubsection>
  <subsubsectiontitle>
    {{- ability.get_title() -}}
    <indexentry>{{- ability.get_title() }} Ability</indexentry> 
    <indexentry>Ability<subentry>{{- ability.get_title() }}</subentry></indexentry>
  </subsubsectiontitle>

  {%- if ability.slug -%}
  {{ ability.slug }}
  {% endif -%}
  
  <p>
    <smaller>
      {% if ability.untrained_rank  %}
      <bold>Untrained:</bold> {{ ability.untrained_rank }} 
      {% endif -%}
      <bold>Ranks:</bold> {{ ability.get_ability_rank_range() }}
      <newline/>
      {%- if ability.prerequisites -%}
      <bold>Prereqs:</bold> {{ ability.get_prerequisites_str() }}
      <newline/>
      {%- endif -%}
      {%- if ability.specializations -%}
      <bold>Specializations:</bold> {{ ability.get_specializations_str() }}
      <newline/>
      {%- endif %}      
      {%- if ability.get_checks() -%}
      <bold>Checks:</bold>
      <indent>
      {%- for check in ability.get_checks() %}
      <abilitybullet/><bold>{{check.name}} ({{check.check_type}})</bold>
      <newline/>
      <bold>Default DC:</bold> {{check.dc}}
      {%- if check.has_advantage() %} with advantage{% endif %}
      {%- if check.has_disadvantage() %} with disadvantage{% endif -%}
      <newline/>
      <bold>Crit Class:</bold> {{ check.crit_class }}<newline/>
      <bold>Action Cost:</bold> {{ check.ap_cost }}
      {% if check.keywords %}
      <bold>Keywords:</bold> {{ check.get_keywords_str() }}
      {% endif %}
      {% if check.range -%}
      <bold>Range:</bold> {{ check.range }}
      {% endif %}
      {% if check.trigger -%}
      <bold>Trigger:</bold> {{ check.trigger }}
      {% endif %}
      {% if check.effect -%}
      <bold>Effect:</bold> {{ check.effect }}
      {% endif %}
      {%- if check.any_success -%}
      <bold>Any-Success:</bold>{{ check.any_success }}<newline/>
      {%- endif -%}
      {% if check.critsuccess -%}
      <bold>Critical Success:</bold> {{ check.critsuccess }}<newline/>
      {%- endif %}
      {%- if check.righteoussuccess -%}
      <bold>Righteous Success:</bold> {{ check.righteoussuccess }}<newline/>
      {%- endif %}
      {% if check.success -%}
      <bold>Success:</bold> {{ check.success }}<newline/>
      {%- endif -%}
      {% if check.any_fail -%}
      <bold>Any-Fail:</bold> {{ check.any_fail }}<newline/>
      {%- endif %}
      {%- if check.fail -%}
      <bold>Fail:</bold> {{ check.fail }}<newline/>
      {%- endif %}
      {%- if check.grimfail -%}
      <bold>Grim Fail:</bold> {{ check.grimfail }}<newline/>
      {%- endif %}
      {%- if check.critfail -%}
      <bold>Critical Fail:</bold> {{ check.critfail }}<newline/>
      {%- endif -%}
      {% if check.blessed -%}
      <bold>Blessed:</bold> {{ check.boon }}<newline/>
      {%- endif %}
      {% if check.boon -%}
      <bold>Boon:</bold> {{ check.boon }}<newline/>
      {%- endif %}
      {% if check.indifferent -%}
      <bold>Indifferent:</bold> {{ check.indifferent }}<newline/>
      {%- endif %}
      {% if check.bane -%}
      <bold>Bane:</bold> {{ check.bane }}<newline/>
      {%- endif %}
      {% if check.damned -%}
      <bold>Damned:</bold> {{ check.damned }}<newline/>
      {%- endif %}            
      {%- endfor -%}
      </indent>
      {%- endif %}            
    </smaller>
  </p>
  {{ ability.description }}  
</subsubsection>
{% endmacro %}
