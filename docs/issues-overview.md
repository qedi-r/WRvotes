---
title: Election Issue Backgrounders
layout: page
---

Election Issue Backgrounders
===============

{::options parse_block_html="true" /}
<div class="flex gutters">

<div class="aside">
<aside class="aside-box" data-aos="fade-left">
* table of contents
{:toc}
</aside>
</div>

<div class="main">

Here are a few topics that have come up frequently during the election. 
This list is not comprehensive; it mentions a few widely discussed issues, along 
with a few pointers to background information. 

{% assign issue-categories = site.data.sync.issue-categories %}

{% for cat in issue-categories %}

{{ cat.IssueCategoryDesc }}
------


  {% include desc-issues-gross.html
     category=cat.IssueCategory %}

  {% include list-issue-media.html
     tag=cat.IssueCategory %}

{% endfor %}

</div>
