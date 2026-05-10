This post mentioned the following module(s):

|Module Code|Module Title|Study Level|Credits|Next Start|
|:-|:-|:-|:-|:-|
% for module in modules:
|[${module.module_code}](${module.url})|[${module.module_title}](${module.url})|${module.ou_study_level}|${module.credits}|${module.next_start.strftime('%Y-%m-%d') if module.next_start else 'Not available'}|
% endfor

---
^(I'm a bot — summon me with ! followed by a module code, e.g. !TM112)
