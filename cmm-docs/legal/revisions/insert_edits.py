"""
Insert proposed edits from operating-agreement.md into the Word doc as red text.
Each edit is inserted as a new paragraph BEFORE the original text it modifies.
"""

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import copy

INPUT = "/Users/atreyu/Documents/GitHub/classic-motor-market/cmm-docs/legal/revisions/CLASSIC MOTOR MARKET LLC -- OPERATING AGREEMENT.docx"
OUTPUT = "/Users/atreyu/Documents/GitHub/classic-motor-market/cmm-docs/legal/revisions/CLASSIC MOTOR MARKET LLC -- OPERATING AGREEMENT (with edits).docx"

RED = RGBColor(0xCC, 0x00, 0x00)
FONT_NAME = "Times New Roman"
FONT_SIZE = Pt(11)

doc = Document(INPUT)

# Each edit: (paragraph_index, edit_label, proposed_text, explanation)
# paragraph_index = index in doc.paragraphs where the ORIGINAL text lives
# We insert the red edit paragraph BEFORE that index

edits = [
    # Edit 1: Effective date
    (3, "EDIT 1",
     "Proposed Edit: Fill in the specific day for January 2026.",
     "The effective date must be completed before signing."),

    # Edit 2: Deadlock auto-dissolution → mediation/arbitration
    (54, "EDIT 2",
     'Proposed Edit: Replace auto-dissolution language with: "...If no Member exercises their rights set forth in Section 11.13 below within seventy-five (75) days after the occurrence of a Deadlock, the Members shall submit the matter to non-binding mediation with a mutually selected mediator. If mediation does not resolve the deadlock within sixty (60) days, the Members shall submit the matter to binding arbitration in Colorado. The Company shall not be dissolved solely on account of a deadlock unless the Members unanimously agree to dissolution or arbitration results in a dissolution order."',
     "The current draft auto-dissolves the company if no one triggers the buy-sell mechanism within 75 days. That's an extreme default — a temporary disagreement could wipe out the company and everyone's equity if no one acts in time. What we actually agreed to (agreement-essentials §15) was: good-faith negotiation → mediation → arbitration. Dissolution should be a last resort that requires unanimous consent, not an automatic trip wire. None of us want a situation where a deadlock window expiring forces a liquidation no one asked for."),

    # Edit 3: Service Obligations — vague, Board-controlled
    (62, "EDIT 3",
     'Proposed Edit: [DECISION REQUIRED] Replace with: "The Founding Members shall perform the services described in Schedule B (Roles and Responsibilities) attached hereto and incorporated herein by reference. Schedule B shall set forth each Founding Member\'s primary responsibilities and may be amended only by unanimous written consent of the Founding Members."',
     "The current draft leaves all of our Service Obligations entirely undefined — the Board decides \"from time to time\" what each of us must do. That means any two of us could expand the third's obligations by majority vote without that person's agreement, and then declare them in Default for not meeting a standard that was never written down when we signed. Our essentials (§4) had detailed per-person roles — those should be in a referenced Schedule so there's a written baseline we all agreed to."),

    # Edit 4: IP assignment — narrowed to CMM's active marketplace only
    (64, "EDIT 4",
     'Proposed Edit: "...all intellectual property work product created specifically for CMM\'s actively operating marketplace shall be Company Intellectual Property, including: the Classic Motor Market platform, brand assets, trademarks, domains, production codebases, customer data, and proprietary workflows built for CMM\'s current operations (the \'Company Intellectual Property\'), are \'works for hire.\' Company Intellectual Property is strictly limited to work created during time expressly dedicated to CMM that directly serves CMM\'s currently active products and services. For the avoidance of doubt, Company Intellectual Property does NOT include: (i) work created outside of CMM-dedicated time; (ii) general-purpose code libraries, frameworks, reusable components, or development patterns not built exclusively for CMM; (iii) skills, experience, and know-how; or (iv) any work conceived or developed in connection with a Separate Permitted Venture (as defined below). The broad definition of \'Company Business\' in this Agreement describes the scope of CMM\'s potential market — it does not expand the IP assignment clause to cover work any Member creates in areas CMM has not yet entered or is not currently operating."',
     "Our concern here is concurrent and future work — not previous code. The way this is currently written, anything any of us builds that could relate to vehicles, boats, aircraft, or bikes belongs to CMM just because the 'Company Business' definition is written to cover all of those. That's a land grab on all of our future work using a definition that was written to protect CMM's expansion potential, not to claim our independent projects. We need the IP assignment to be tied to what we actually build FOR CMM's current marketplace, not to what CMM might someday enter. If any of us is building something that isn't competing with what CMM is actively doing right now, it belongs to that person."),

    # Edit 5: "Separate Permitted Venture" — defined + Rebuild Provision
    (66, "EDIT 5",
     'Proposed Edit: Replace with: "Notwithstanding the foregoing, the Members acknowledge and agree that: (a) any work product conceived, developed, created, or reduced to practice by any Member in connection with any Separate Permitted Venture (the \'Separate Intellectual Property\') shall not be deemed \'Company Intellectual Property\'; (b) personal contact lists, professional networks, and industry relationships belonging to any Member are not Company Intellectual Property regardless of whether those contacts become customers or vendors of the Company; and (c) a departing Member may build a new product from scratch in any industry — including automotive — provided such Member does not copy Company source code, use Company confidential information, or launch a product that directly replicates CMM\'s currently active marketplace operations (\'Rebuild Provision\'). A \'Separate Permitted Venture\' means any business, project, or endeavor: (i) that does not directly compete with CMM\'s currently active marketplace operations; (ii) that does not use Company Confidential Information; and (iii) that does not use Company source code or CMM customer data. Whether a venture \'directly competes\' is evaluated against what CMM is actually operating at the time — not against the broad \'Company Business\' definition."',
     "The term 'Separate Permitted Venture' appears in the original as a carve-out but is never defined — which makes it worthless. Without a definition, anything any of us builds could be claimed as Company IP because there's no legal standard for what a 'separate permitted venture' actually is. Our bigger concern here isn't previous code — it's concurrent and future projects. We need a clear definition that ties the competition test to what CMM is actually doing, not what the broad definition says CMM could someday do. The Rebuild Provision is also critical: any of us needs to be able to build something new after leaving, even in automotive, as long as we're not cloning CMM's current marketplace."),

    # Edit 6: Non-compete start date
    (78, "EDIT 6",
     'Proposed Edit: "...for the period commencing on the date such Member\'s active Service Obligations terminate and expiring one (1) year after such date (the \'Restricted Period\')..."',
     "The non-compete currently starts on the date we sign this agreement, not the date any of us leaves. That means the restricted period clock starts running today, even though we're all still actively working for CMM. The one-year post-departure window is fine — but it should start when a member actually leaves, not when we sign. Also, the non-compete applies \"with or without cause\" — so even if one of us is wrongfully forced out, the full restriction hits that person. That's not acceptable. If any of us is removed without cause, that person shouldn't be penalized on top of it."),

    # Edit 7: Non-compete scope
    (80, "EDIT 7",
     'Proposed Edit: "Participate or engage, directly or indirectly, in operating a curated online paid marketplace for classic or enthusiast automobiles that directly competes with CMM\'s currently active marketplace operations. \'Directly competes\' means targeting the same seller and buyer segment with a substantially similar marketplace product to what CMM is actively operating at the relevant time. This restriction does not prohibit any Member from: (i) working in automotive software, engineering, or technology in any capacity that is not a direct marketplace competitor; (ii) building software platforms, tools, or applications in any industry; (iii) working in aviation, marine, motorcycle, bicycle, or any other vehicle or mobility sector; (iv) building or joining a company in any space CMM has not yet entered or is not currently operating in; or (v) working as an employee, contractor, consultant, or investor in any adjacent industry."',
     "The non-compete as written uses 'Company Business' as the competitive boundary — but that definition covers boats, aircraft, motorcycles, and every wheeled vehicle, not just the classic car marketplace we actually built. That's not a fair reflection of what any of us agreed not to compete with. We're all fine not running a direct competitor to CMM's actual current marketplace while we're members and for a year after leaving. What we're not okay with is being blocked from automotive software, adjacent tech, or industries CMM hasn't entered just because a lawyer wrote a broad definition. The restriction should follow what CMM actually does, and if CMM expands into new areas in the future, that's when those areas become relevant — not before."),

    # Edit 8: Disparagement clause
    (88, "EDIT 8",
     'Proposed Edit: Remove this provision entirely, or narrow to: "Make false and defamatory statements of fact about the Company with knowledge of their falsity."',
     "A blanket ban on \"disparaging the Company or conditions of employment\" means none of us can honestly talk about our experience, our work conditions, or why we left — even after we're gone. That seems excessive. Narrowing this to actually false defamatory statements is fair — and we think that's illegal anyway. None of us would want to lie regardless."),

    # Edit 9: Good Leaver waiver
    (98, "EDIT 9",
     'Proposed Edit: Add after the forfeiture clause: "Notwithstanding the foregoing, upon written request by the departing Founding Member, the remaining Founding Members shall review the circumstances of an Early Departure and may waive some or all of the foregoing forfeiture by majority vote (i.e., both remaining Founding Members) if they determine in good faith that such departure qualifies as a \'Good Leaver\' event. A \'Good Leaver\' event includes departure due to: (i) serious health reasons or disability; (ii) family relocation requiring departure from the region; (iii) mutual agreement of the remaining Members; (iv) role redundancy as reasonably determined by the remaining Members; or (v) other compelling circumstances determined by the remaining Members in good faith. If the remaining Members cannot agree on Good Leaver status, the departing Member may submit the determination to binding arbitration in Colorado. In the event of a Good Leaver determination, the Company or remaining Members shall have the option to repurchase the vested equity at fair market value as determined by an independent appraiser. Absent a Good Leaver determination (by agreement or arbitration), the automatic forfeiture provisions of this Section shall apply."',
     "The current draft makes the 50% forfeiture automatic for any early departure, no exceptions. That means if any of us leaves because of a serious health issue, a family emergency, or anything else completely outside our control, that person loses half their equity with no recourse. We deliberately negotiated a Good Leaver review into our essentials (§10) and the lawyer simply dropped it. We need the ability for a departing founder to request a review and have the remaining founders make a good-faith determination — and if they can't agree, take it to arbitration. The forfeiture is appropriate as a default, but there has to be a path for legitimate circumstances."),

    # Edit 10: Gross negligence Default trigger
    (102, "EDIT 10",
     'Proposed Edit: "commits acts of willful misconduct that are likely to materially harm the Company Business, any other Members, and/or any Customers; provided, however, that no Default based on alleged gross negligence shall be deemed to occur unless: (i) the non-defaulting Founding Members provide written notice specifically describing the acts constituting such gross negligence; (ii) the accused Member has thirty (30) days to cure or respond in writing; and (iii) the remaining Founding Members unanimously agree in writing that the conduct constitutes gross negligence after reviewing the response."',
     "\"Gross negligence\" is completely subjective — any judgment call any of us makes (architecture decisions, financial trade-offs, marketing strategy) could be labeled gross negligence. There's no written notice, no cure period, no evidence standard required before this Default trigger fires. Any two of us could disagree with a decision the third made, call it gross negligence, and use that to start a forced buyout. We need this to require written notice, a cure period, and unanimous agreement — the same standard every other Default trigger has."),

    # Edit 11: Manager removal — for Cause only
    (135, "EDIT 11",
     'Proposed Edit: Add a new section: "Removal for Cause. No Founding Member may be removed as a Manager except for Cause. \'Cause\' shall be strictly limited to: (i) fraud; (ii) criminal conduct involving moral turpitude; (iii) willful misconduct materially harmful to the Company; (iv) material breach of this Agreement following written notice and failure to cure within thirty (30) days; or (v) misappropriation of Company assets or intellectual property. Removal for Cause shall require the unanimous written consent of the non-impacted Founding Members. Removal of a Founding Member as Manager without Cause is expressly prohibited. A Founding Member removed for Cause shall be subject to the Bad Leaver provisions of this Agreement."',
     "There's no standalone protection in this draft against any of us being removed as a Manager without cause. The only removal mechanism is automatic — after a Default redemption. But who triggers that Default? The other two founders, by majority vote. So any two of us could declare the third in Default using vague grounds like \"gross negligence\" or undefined Service Obligations, vote to redeem their units, and automatically remove them from the Board — all without any independent Cause determination. Our essentials (§20) explicitly prohibited this and defined Cause narrowly. We need that protection in the agreement before any of us signs it."),

    # Edit 12: Spending authority $300 → $500
    (164, "EDIT 12",
     'Proposed Edit: "...no Manager shall spend or authorize spending more than $500 without the majority approval of the Board."',
     "We all agreed on $500 in our essentials (§5). The lawyer used $300 instead."),

    # Edit 13: Partnership Representative — name Michael Burroughs
    (242, "EDIT 13",
     'Proposed Edit: "Michael Burroughs is hereby designated the \'Partnership Representative\' of the Company..."',
     "Michael handles daily business and financial operations per our essentials (§4), so he's the right person to interface with the IRS. This blank must be filled before we sign, and we all agree Michael is the logical choice given his role."),

    # Edit 14: Secondary ROFR
    (328, "EDIT 14",
     'Proposed Edit: After the Company ROFR provision, add: "In the event the Company does not exercise its right of first refusal within the applicable 30-day period, the remaining Founding Members (excluding the Withdrawing Member) shall have a secondary right of first refusal, exercisable within thirty (30) days following the Company\'s declination, to purchase the Withdrawing Member\'s interest on the same price, terms, and conditions set forth in the Sale Notice, pro rata based on their respective Percentage Interests. If the remaining Members do not exercise this secondary right within such 30-day period, the Withdrawing Member may proceed with the sale to the Third Party Purchaser subject to the terms of this Agreement."',
     "Our essentials (§8) gave the Company first right of refusal, then a secondary right to the remaining members. The lawyer dropped the secondary member ROFR — so if the Company passes, the stake goes straight to a stranger. Any of us could end up in business with someone we've never met if another founder sells out and the Company doesn't exercise its right. The secondary ROFR gives the remaining founders a chance to buy before that happens."),

    # Edit 15: Voluntary departure payment terms
    (352, "EDIT 15",
     'Proposed Edit: "...the Company shall pay to such Terminating Member the Redemption Price, at the election of the Company, either: (i) in full in cash at closing; or (ii) twenty-five percent (25%) of the Redemption Price in cash at closing and the balance in equal annual payments on each anniversary of the date of such closing amortized over four (4) years with interest thereon accruing at the Prime Rate during the 30-day period prior to the date of such closing."',
     "If any of us leaves voluntarily, the Company can choose to pay nothing at closing and stretch the rest over 10 years at below-market interest. These terms need to be equalized with the disabled/deceased member structure so that a voluntary departure isn't treated worse than death or disability on payment timeline."),

    # Edit 16: Bad Leaver — 25% price discount + 10% down, 4-year payment
    (358, "EDIT 16",
     'Proposed Edit: Two changes: (1) Payment terms — replace 0%/10-year with: "ten percent (10%) of the Redemption Price in cash at closing and the balance in equal annual payments on each anniversary of such closing amortized over four (4) years, with interest thereon accruing at the Prime Rate during the 30-day period prior to the date of such closing." (2) Price — add: "the Redemption Price applicable to a Defaulting Member shall be calculated as seventy-five percent (75%) of the Current Value (a 25% discount from fair market value). This discount applies only to confirmed Defaulting Members and shall not take effect until the Default determination is final."',
     "The 25% price discount is the real penalty for being a Bad Leaver — that's the financial consequence for causing harm to the company. The 0%/10-year payment structure on top of it is punishing twice, and 10 years is a long time to be owed money with no guarantee of collection. 10% down with 4-year amortization is what the document already gives to disabled and deceased founders — there's no reason a Bad Leaver should be treated worse on payment timeline than a deceased founder. The discount does the heavy lifting. The payment terms just need to be clean and consistent."),

    # Edit 17: Jury trial waiver → AAA arbitration
    (398, "EDIT 17",
     'Proposed Edit: Remove jury trial waiver entirely. Retitle section "Governing Law; Venue; Jurisdiction." Replace with: "Any dispute arising under this Agreement shall be resolved by binding arbitration administered by the American Arbitration Association under its Commercial Arbitration Rules, seated in Boulder, Colorado. The arbitrator shall have authority to award any remedy available at law or in equity."',
     "This wasn't in our essentials at all. A blanket jury trial waiver means every dispute — IP ownership, wrongful default, forced buyout — goes to a judge with no jury. That favors whoever has more legal firepower, which in a dispute against the Company would be the Company. What we actually agreed to in our essentials was mediation → arbitration, which is a better path anyway. None of us should be signing away our right to a jury trial in a standalone waiver that serves no purpose other than tilting disputes toward whoever can afford to outspend the other side."),

    # Edit 18: Amendment authority — unanimous Member consent
    (406, "EDIT 18",
     'Proposed Edit: "...the provisions of this Agreement and the Articles may be amended only upon the unanimous written consent of all Founding Members acting in their capacity as Members (not solely as Board members)."',
     "This matters because of the sequence: if any one of us is removed as a Manager first (using Default or other grounds), that person loses their Board vote. Then the remaining two could amend the agreement by \"unanimous Board vote\" with only two people left on the Board. Tying amendments to Member consent — not Board status — means every founder retains their amendment veto as long as they're a Member, regardless of whether they've been removed as a Manager. Our essentials (§21) were clear: unanimous written consent of the Members. That's the standard this should match."),

    # Edit 19: H&C conflict waiver — DELETE subsection (d)
    (410, "EDIT 19",
     'Proposed Edit: DELETE SUBSECTION (d) ENTIRELY. Do not replace it. The remainder of the Acknowledgements section (subsections a, b, c) can stay, but subsection (d) must be removed with no substitution.',
     "This is the most dangerous clause in the document for all of us. By signing this, each of us is pre-emptively waiving our right to challenge Hutchinson Black & Cook as counsel in any future dispute — including one where the Company or the Board is directly adverse to one of us individually. That means the same law firm that drafted this agreement could represent the Company against any one of us in an IP dispute, Default proceeding, or forced buyout, and that person would have already agreed they can't object. That's an extraordinary concession none of us agreed to in our essentials. We need subsection (d) deleted entirely — not narrowed, deleted. We should also each strongly consider getting independent legal counsel to review this agreement before signing."),

    # Edit 20: Company Business definition — dynamic
    (439, "EDIT 20",
     'Proposed Edit: "The \'Company Business\' shall mean, as of any date of determination, the business CMM is actively operating at that time, which as of the Effective Date is a curated online paid marketplace for classic and enthusiast automobiles. \'Company Business\' expands only as CMM actually enters and operates in new markets — it does not pre-emptively cover markets CMM may someday enter based on this or any other broad definition. For the avoidance of doubt, the following are never included in \'Company Business\' unless CMM is actively operating them at the time of determination: (i) aviation or aerospace; (ii) marine or boating; (iii) motorcycles, bicycles, or micromobility; (iv) software tools, engineering platforms, or automotive technology services not functioning as a curated marketplace; or (v) any market, product, or industry in which CMM has not launched an active commercial product."',
     "This is the definition we care most about because it controls both what IP we assign to CMM and what we're restricted from competing with. The way the lawyer wrote it, the definition is a forward-looking land grab — it lists every vehicle category CMM could conceivably expand to, and uses that aspirational scope to claim all of our future work and restrict our careers. That's not what we agreed to. What we're okay with: not competing with CMM's actual current marketplace while we're here, and for a year after any of us leaves. What we're not okay with: being restricted from automotive software, boat tech, aviation tools, or motorcycle apps just because a lawyer listed them in a definition. This proposed edit makes the definition dynamic — it describes what CMM actually does, and only expands if CMM actually enters those markets. That's fair to everyone."),

    # Edit 21: Exhibit A — complete
    (499, "EDIT 21",
     'Proposed Edit: Exhibit A must be completed before signing:\n\nAtreyu Sutton — $1,000 capital contribution — 3,000 Membership Units\nBrian Hughes — $1,000 capital contribution — 3,000 Membership Units\nMichael Burroughs — $1,000 capital contribution — 3,000 Membership Units\nTotal: $3,000 capital — 9,000 Units\n\nThe date on Exhibit A must match the Agreement\'s effective date (January [DAY], 2026).',
     "Everything — Capital Accounts, tax distributions, ownership percentages — depends on Exhibit A."),
]


def add_red_paragraph_before(doc, para_index, label, proposed, explanation):
    """Insert a red-text edit paragraph before the given paragraph index."""
    target_para = doc.paragraphs[para_index]
    # Get the parent element and insert a new paragraph element before the target
    parent = target_para._element.getparent()

    # Build the text
    text = f"[{label}]\n{proposed}\nExplanation: {explanation}"

    # Create new paragraph by adding after the previous element
    from docx.oxml.ns import qn
    from lxml import etree

    new_p = copy.deepcopy(target_para._element)
    # Clear all content from the copied paragraph
    for child in list(new_p):
        new_p.remove(child)

    # Remove any style that would make it a heading, keep it Normal
    pPr = new_p.find(qn('w:pPr'))
    if pPr is not None:
        pStyle = pPr.find(qn('w:pStyle'))
        if pStyle is not None:
            pPr.remove(pStyle)

    # Create a run with red text
    run_elem = etree.SubElement(new_p, qn('w:r'))
    rPr = etree.SubElement(run_elem, qn('w:rPr'))

    # Font name
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), FONT_NAME)
    rFonts.set(qn('w:hAnsi'), FONT_NAME)

    # Font size (11pt = 22 half-points)
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '22')
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), '22')

    # Red color
    color = etree.SubElement(rPr, qn('w:color'))
    color.set(qn('w:val'), 'CC0000')

    # Bold for the label
    b = etree.SubElement(rPr, qn('w:b'))

    # Split text into label line and rest
    lines = text.split('\n', 1)
    label_text = lines[0]
    rest_text = lines[1] if len(lines) > 1 else ""

    # Set label text (bold)
    t = etree.SubElement(run_elem, qn('w:t'))
    t.set(qn('xml:space'), 'preserve')
    t.text = label_text

    # Add line break + rest of text (not bold)
    if rest_text:
        # Line break
        br = etree.SubElement(run_elem, qn('w:br'))

        # New run for the non-bold text
        run_elem2 = etree.SubElement(new_p, qn('w:r'))
        rPr2 = etree.SubElement(run_elem2, qn('w:rPr'))

        rFonts2 = etree.SubElement(rPr2, qn('w:rFonts'))
        rFonts2.set(qn('w:ascii'), FONT_NAME)
        rFonts2.set(qn('w:hAnsi'), FONT_NAME)

        sz2 = etree.SubElement(rPr2, qn('w:sz'))
        sz2.set(qn('w:val'), '22')
        szCs2 = etree.SubElement(rPr2, qn('w:szCs'))
        szCs2.set(qn('w:val'), '22')

        color2 = etree.SubElement(rPr2, qn('w:color'))
        color2.set(qn('w:val'), 'CC0000')

        # Split rest into proposed and explanation, handle newlines
        for i, line in enumerate(rest_text.split('\n')):
            if i > 0:
                br2 = etree.SubElement(run_elem2, qn('w:br'))
            t2 = etree.SubElement(run_elem2, qn('w:t'))
            t2.set(qn('xml:space'), 'preserve')
            t2.text = line

    # Insert before target
    parent.insert(list(parent).index(target_para._element), new_p)

    # Also insert an empty paragraph after the edit (separator)
    sep_p = copy.deepcopy(new_p)
    for child in list(sep_p):
        sep_p.remove(child)
    parent.insert(list(parent).index(target_para._element), sep_p)


# Process edits in REVERSE order so indices don't shift
for para_idx, label, proposed, explanation in reversed(edits):
    print(f"Inserting {label} before paragraph {para_idx}...")
    add_red_paragraph_before(doc, para_idx, label, proposed, explanation)

doc.save(OUTPUT)
print(f"\nSaved to: {OUTPUT}")
