*Beep-boop - I'm a bot!*

I see you've mentioned some OU modules. I've pulled together some information on these modules for your convenience.

% for module in modules:
---

<%text>###</%text> ${module.module_code}
<%text>####</%text> _${module.module_title}_

|Credits|Study Level|Next start|Next end|
|:-|:-|:-|:-|
|${module.credits}|${module.ou_study_level}|${module.next_start.strftime('%Y-%m-%d') if module.next_start else 'Not available'}|${module.next_end.strftime('%Y-%m-%d') if module.next_end else 'Not available'}|

% if module.related_qualifications and len(module.related_qualifications[0].strip()) > 0:
<%text>#####</%text> Related Qualifications

% for qualification in module.related_qualifications:
- ${qualification}

% endfor
% endif
<%text>#####</%text> Course work includes:
% for requirement in module.course_work_includes:
- ${requirement}

% endfor

[View module on OU website](${module.url})

% endfor
---

^(This content was generated using information taken from the OU.)

^(I'm open source, view my) [^source ^code. ](http://github.com/jmcharter/ou_module_bot) ^(To report issues,) [^send ^me
^a ^message. ](https://old.reddit.com/message/compose?to=${user}&subject=Issue%20Report&message=)
