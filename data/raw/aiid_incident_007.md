Source: AI Incident Database, https://incidentdatabase.ai/cite/7
Incident ID: 7
Title: Wikipedia Vandalism Prevention Bot Loop
Reported dates: February 23-24, 2017

Description: Wikipedia's automated editing bots, designed to remove
vandalism and maintain article quality, began engaging in repetitive conflict
with one another. These bots would repeatedly undo each other's edits,
creating feedback loops that persisted for extended periods, some conflicts
lasting over a decade. The incident occurred when multiple bots with
different vandalism-detection algorithms made incompatible editorial
decisions. Rather than collaborating toward their shared goal of article
improvement, the bots entered into "edit wars," continuously reversing the
other's changes. The behavior of bots is often unpredictable and sometimes
leads them to produce errors over and over again in a potentially infinite
feedback loop. A notable example involved coordinated vandalism inserting
irrelevant references into unrelated articles around 2006, which triggered
bot responses that themselves became problematic.

Deployer/Platform: Wikipedia (operated by Wikimedia Foundation)
Affected parties: Wikipedia editors and users
AI systems: Multiple unnamed Wikipedia editing bots
Key characteristics: High autonomy, software-only systems operating on
amateur users' platform, with specification, robustness, and assurance
failures identified.
