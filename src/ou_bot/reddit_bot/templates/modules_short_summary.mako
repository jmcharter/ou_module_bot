This post mentioned the following module(s):

|Module Code|Module Title|Study Level|Credits|Next Start|Next End|
|:-|:-|:-|:-|:-|:-|
% for module in modules:
|[${module.module_code}](${module.url})|[${module.module_title}](${module.url})|${module.ou_study_level}|${module.credits}|${module.next_start.strftime('%Y-%m-%d') if module.next_start else 'Not available'}|${module.next_end.strftime('%Y-%m-%d') if module.next_end else 'Not available'}|
% endfor
