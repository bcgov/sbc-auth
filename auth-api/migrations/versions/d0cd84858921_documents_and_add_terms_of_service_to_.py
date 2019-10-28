"""documents and add terms of service to user

Revision ID: d0cd84858921
Revises: b2749f31f268
Create Date: 2019-10-27 06:01:54.359356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0cd84858921'
down_revision = 'b2749f31f268'
branch_labels = None
depends_on = None


def upgrade():
    documents = op.create_table('documents',
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('version_id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=20), nullable=False),
                    sa.Column('content', sa.Text(), nullable=True),
                    sa.Column('created_by_id', sa.Integer(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['modified_by_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('version_id')
                    )
    op.add_column('user', sa.Column('is_terms_of_use_accepted', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('terms_of_use_accepted_version', sa.Integer(), nullable=True))
    op.create_foreign_key('user_documents_fk', 'user', 'documents', ['terms_of_use_accepted_version'], ['version_id'])

    html_content = """<p class="p1"><span class="s1"><strong>COOPERATIVES REGISTRY </strong></span></p>
<p class="p2"><span class="s1"><strong>TERMS AND CONDITIONS OF AGREEMENT</strong></span></p>
<p class="p3"><span class="s1">The parties to this &ldquo;Cooperatives Registry Terms and Conditions of Agreement&rdquo; (the &ldquo;<strong>Agreement</strong>&rdquo;) are Her Majesty the Queen in Right of the Province of British Columbia, as represented by the Minister of Citizens&rsquo; Services (the &ldquo;<strong>Province</strong>&rdquo;) and the Subscriber (as defined below).</span></p>
<ol class="ol1">
<li class="li4"><span class="s2"><strong>DEFINITIONS</strong></span></li>
</ol>
<ol class="ol2">
<li class="li5"><span class="s3">&ldquo;</span><span class="s2"><strong>Access</strong>&rdquo; means the non-exclusive right to electronically access and use the Service;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Basic Account Subscriber&rdquo;</strong> means a Subscriber with Access to up to ten Entities that pays Fees for Transactions using a credit card;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;BC Online Terms and Conditions&rdquo; </strong>means the BC Online Terms and Conditions of Agreement found at <a href="https://www.bconline.gov.bc.ca/terms_conditions.html"><span class="s4">https://www.bconline.gov.bc.ca/terms_conditions.html</span></a>.</span></li>
<li class="li5"><span class="s2"><strong> &ldquo;Content&rdquo;&nbsp;</strong>means the Service&rsquo;s Data Base, and all associated information and documentation, including any print copy or electronic display of any information retrieved from the Data Base and associated with the Service;</span></li>
<li class="li5"><span class="s2">&ldquo;<strong>Data Base&rdquo;</strong> means any data base or information stored in electronic format for which Access is made available through the Service;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Deposit Account&rdquo; </strong>has the meaning given to it in the BC Online Terms and Conditions;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Entity&rdquo;</strong> means any BC co-operative for which a User has Access through the Service;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Fees&rdquo;</strong> means all fees and charges for the Service, as described in the <a href="http://www.bclaws.ca/civix/document/id/complete/statreg/02057_16#Schedule"><span class="s1"><em>Business Corporations Act - Schedule (Section 431) Fees</em></span></a><em>, Cooperative Association Act - </em><a href="http://www.bclaws.ca/civix/document/id/complete/statreg/391_2000#section11"><span class="s1"><em>Cooperative Association Regulation, Schedule A</em></span></a>;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Incorporation Number&rdquo; </strong>means the unique numerical identifier for a Subscriber&rsquo;s cooperative association, and when entered in conjunction with the Passcode, permits a User to access the Service;</span></li>
<li class="li5"><span class="s1">&ldquo;<strong>Passcode</strong>&rdquo; means the unique identifier issued by the Province to a Subscriber with regard to an Entity, which enables a User to have Access with regard to that Entity within the Service; </span></li>
<li class="li5"><span class="s2"> &ldquo;<strong>Premium Account Subscriber</strong>&rdquo; means a Subscriber with Access to unlimited Entities that has a Deposit Account with the Province and is charged Fees in accordance with the BC Online Terms and Conditions;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Service&rdquo;&nbsp;</strong>means the service operated by the Province that allows a Subscriber to completeTransactions relating to BC Entities.</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Services Card Number&rdquo;</strong> means the User&rsquo;s BC Services Card number, which authenticates the identity of the User to the Service; </span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Subscriber&rdquo;</strong> means a person that accesses the Service and that has accepted the terms of this Agreement, and includes Premium Account Subscribers and Basic Account Subscribers;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Transaction&rdquo;</strong> means any action performed by the Subscriber or any of its Users to the Service to display, print, transfer, or obtain a copy of information contained on the Service, or where permitted by the Province, to add to or delete information from the Service.</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;User&rdquo; </strong>means an individual that is granted Access on the individual&rsquo;s behalf, if the individual is also the Subscriber, or on behalf of the Subscriber, if the individual is an employee or is otherwise authorized to act on behalf of the Subscriber, as applicable;</span></li>
<li class="li5"><span class="s2"><strong>&ldquo;Website&rdquo; </strong>means the BC Cooperatives Website at bcregistry.ca/cooperatives <span class="Apple-converted-space">&nbsp; &nbsp; &nbsp; &nbsp; </span>and includes all web pages and associated materials, with the exception of the Content.</span></li>
</ol>
<ol class="ol1">
<li class="li5"><span class="s2"><strong>ACCEPTANCE OF AGREEMENT </strong></span></li>
</ol>
<ol class="ol1">
<ol class="ol1">
<li class="li6"><span class="s1">The Subscriber acknowledges that a duly authorized representative of the Subscriber has accepted the terms of this Agreement on behalf of the Subscriber and its Users.</span></li>
</ol>
</ol>
<p class="p7"><span class="s1"><span class="Apple-converted-space">&nbsp;&nbsp;</span></span></p>
<ol class="ol1">
<ol class="ol1">
<li class="li8"><span class="s1">The Subscriber acknowledges and agrees that:</span></li>
</ol>
</ol>
<p class="p9">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<ol class="ol2">
<li class="li6"><span class="s1">by creating a profile and/or by clicking the button acknowledging acceptance of this Agreement, each User using the Services on behalf of the Subscriber also accepts, and will be conclusively deemed to have accepted, the terms of this Agreement as they pertain to the User&rsquo;s use of the Services; and</span></li>
<li class="li6"><span class="s1">the Subscriber will be solely responsible for its Users&rsquo; use of the Services, including without limitation any Fees incurred by its Users in connection with such Services.</span></li>
</ol>
</ol>
</ol>
<p class="p10">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li5"><span class="s1">The Subscriber acknowledges that the terms of the BC Services Card Login Service found at (<a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/terms-of-use"><span class="s4">https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/terms-of-use</span></a>) continue to apply in respect of use of the Services Card.</span></li>
</ol>
</ol>
<p class="p11">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li5"><span class="s1">Premium Account Subscribers acknowledge that in addition to this Agreement, the terms of the BC Online Terms and Conditions will continue to apply in respect of the use of the Subscriber&rsquo;s Deposit Account for payment of Fees for the Service.</span></li>
</ol>
</ol>
<p class="p11">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li6"><span class="s1">The Subscriber will ensure that each of its Users are aware of and comply with the terms of this Agreement as they pertain to the User&rsquo;s use of the Services.</span></li>
</ol>
</ol>
<p class="p7">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li8"><span class="s1">The Province reserves the right to make changes to the terms of this Agreement at any time without direct notice to either the Subscriber or its Users, as applicable.<span class="Apple-converted-space">&nbsp; </span>The Subscriber acknowledges and agrees that it is the sole responsibility of the Subscriber to review, and, as applicable, to ensure that its Users review, the terms of this Agreement on a regular basis.&nbsp;</span></li>
</ol>
</ol>
<p class="p9">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li8"><span class="s1">Following the date of any such changes, the Subscriber will be conclusively deemed to have accepted any such changes on its own behalf and on behalf of its Users, as applicable.<span class="Apple-converted-space">&nbsp; </span>The Subscriber acknowledges and agrees that each of its Users must also accept any such changes as they pertain to the User&rsquo;s use of the Services.</span></li>
</ol>
</ol>
<p class="p12">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>PROPRIETARY RIGHTS</strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">The Website and the Content is owned by the Province and/or its licensors and is protected by copyright, trademark and other laws.<span class="Apple-converted-space">&nbsp; </span>Except as expressly permitted in this Agreement, the Subscriber may not use, reproduce, modify or distribute, or allow any other person to use, reproduce, modify or distribute, any part of the Website in any form whatsoever without the prior written consent of the Province. </span></li>
</ol>
</ol>
<p class="p13">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>SERVICES</strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">The Province will provide the Subscriber and its Users with Access on the terms and conditions set out in this Agreement.</span></li>
<li class="li6"><span class="s1">Subject to section 3.3, Access will be available during the hours published on the Website, as may be determined by the Province in its sole discretion from time to time.&nbsp;</span></li>
<li class="li6"><span class="s1">The Province reserves the right to limit or withdraw Access at any time in order to perform maintenance of the Service or in the event that the integrity or security of the Service is compromised.</span></li>
<li class="li6"><span class="s1">The Province further reserves the right to discontinue the Service at any time.</span></li>
<li class="li6"><span class="s1">The Province will provide helpdesk support to assist Users with Access </span><span class="s2">during the hours published on the Website</span><span class="s1">, as may be determined by the Province in its sole discretion from time to time.</span></li>
<li class="li6"><span class="s1">The Subscriber acknowledges and agrees that, for the purpose of Access:</span></li>
</ol>
</ol>
<ol class="ol2">
<li class="li6"><span class="s1">it is the Subscriber&rsquo;s sole responsibility, at the Subscriber&rsquo;s own expense, to provide, operate and maintain computer hardware and communications software or web browser software that is compatible with the Services; and</span></li>
<li class="li6"><span class="s1">that any failure to do so may impact the Subscriber&rsquo;s and/or User&rsquo;s ability to access the Service.</span></li>
</ol>
<p class="p14">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>SUBSCRIBER OBLIGATIONS</strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">The Subscriber will comply, and will ensure that all of its Users comply, with:</span></li>
</ol>
</ol>
<ol class="ol2">
<li class="li6"><span class="s1">the requirements regarding the integrity and/or security of the Service set out in this Article 4; and</span></li>
<li class="li6"><span class="s1">all applicable laws</span></li>
</ol>
<p class="p15"><span class="s1">in connection with the Subscriber&rsquo;s and/or Users&rsquo; use of the Services.&nbsp;</span></p>
<ol class="ol1">
<ol class="ol1">
<li class="li6"><span class="s1">The Subscriber will ensure that each User:</span></li>
</ol>
</ol>
<ol class="ol1">
<ol class="ol1">
<ol class="ol2">
<li class="li6"><span class="s1">is duly authorized by the Subscriber to perform any Transaction and utilize the Service on behalf of the Subscriber;</span></li>
<li class="li6"><span class="s1">maintains in confidence Services Card Numbers, Incorporation Numbers and Passcodes; </span></li>
<li class="li6"><span class="s1">is competent to perform a Transaction and utilize the Service; </span></li>
<li class="li6"><span class="s1">has been adequately trained and instructed to perform a Transaction and utilize the Service; and</span></li>
<li class="li6"><span class="s1">does not use the Service for any inappropriate or unlawful purpose.</span></li>
</ol>
</ol>
</ol>
<p class="p14">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>FEES </strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">The Subscriber will pay to the Province all applicable Fees for the Services. </span></li>
<li class="li6"><span class="s1">Fees payable for Transactions processed by Premium Account Subscribers will be charged to the applicable Deposit Account and in accordance with the BC Online Terms and Conditions.</span></li>
<li class="li8"><span class="s1">Fees payable for Transactions processed by Basic Account Subscribers will be payable by credit card before the Transaction is processed.</span></li>
</ol>
</ol>
<p class="p14">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>RELATIONSHIP</strong></span></li>
<ol class="ol1">
<li class="li8"><span class="s1">This Agreement will not in any way make the Subscriber or any User an employee, agent or independent contractor of the Province and the Subscriber will not, and will ensure that its Users do not, in any way indicate or hold out to any person that the Subscriber or any User is an employee, agent or independent contractor of the Province.</span></li>
</ol>
</ol>
<p class="p14">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>SUSPENSION OF SERVICE </strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">The Province may, in its sole discretion, immediately suspend Access upon written notice to the Subscriber if:</span></li>
</ol>
</ol>
<ol class="ol2">
<ol class="ol2">
<ol class="ol2">
<li class="li6"><span class="s1">the Subscriber or any of its Users has, in the reasonable opinion of the Province, in any way jeopardized the integrity or security of the Service; or</span></li>
<li class="li8"><span class="s1">the Subscriber or any of its Users has violated any other provision of this Agreement.</span></li>
</ol>
</ol>
</ol>
<p class="p14">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>TERMINATION</strong></span></li>
</ol>
<p class="p16">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li6"><span class="s1">The Province may immediately terminate this Agreement upon written notice to the Subscriber if the Subscriber&rsquo;s Access has been suspended pursuant to section 7.1.</span></li>
<li class="li6"><span class="s1">Upon termination:</span></li>
<ol class="ol2">
<li class="li6"><span class="s1">the Subscriber will immediately cease, and will ensure that all of its Users immediately cease, all use of the Service and all Passcodes; and</span></li>
<li class="li6"><span class="s1">Premium Account Subscribers will pay to the Province all unpaid Fees incurred by the Subscriber up to the date of termination.</span></li>
</ol>
<li class="li8"><span class="s1">In the event that a Subscriber&rsquo;s Agreement is terminated, the Province reserves the right to refuse future Access to that Subscriber or to downgrade a Premium Account Subscriber to a Basic Account Subscriber, in which case the Subscriber acknowledges and agrees that it is only entitled to Access up to ten Entities and will release any Entities in excess of that number.</span></li>
</ol>
</ol>
<p class="p13">&nbsp;</p>
<ol class="ol1">
<li class="li6"><span class="s1"><strong>WARRANTY DISCLAIMER, LIMITATION OF LIABILITY AND INDEMNITY</strong></span></li>
<ol class="ol1">
<li class="li6"><span class="s1">THE SUBSCRIBER<span class="Apple-converted-space">&nbsp; </span>ACKNOWLEDGES AND CONFIRMS THAT THE SUBSCRIBER UNDERSTANDS THAT THIS ARTICLE 10 REQUIRES THE SUBSCRIBER TO ASSUME THE FULL RISK IN RESPECT OF ANY USE OF THE SERVICES BY THE SUBSCRIBER AND/OR ITS USERS.</span></li>
<li class="li6"><span class="s1">Except as expressly set out in this Agreement, and in addition to the Province&rsquo;s general <a href="http://www2.gov.bc.ca/gov/admin/disclaimer.page"><span class="s4">Warranty Disclaimer</span></a><a href="https://www2.gov.bc.ca/gov/content/home/disclaimer"><span class="s4"> and Limitation of Liabilities</span></a>,</span> <span class="s1">the Province assumes no responsibility or liability to any person using the Service or any Content.<span class="Apple-converted-space">&nbsp; </span>In particular, without limiting the general nature of the foregoing:</span></li>
</ol>
</ol>
<ol class="ol1">
<ol class="ol1">
<ol class="ol2">
<li class="li6"><span class="s1">in no event will the Province, its respective servants, agents, contractors or employees be liable for any direct, indirect, special or consequential damages or other loss, claim or injury, whether foreseeable or unforeseeable (including without limitation claims for damages for personal injury, lost profits, lost savings or business opportunities) arising out of or in any way connected with the use of, or inability to use the Service or any Content;</span></li>
<li class="li6"><span class="s1">the entire risk as to the quality and performance of the Service or any Content, is assumed by the Subscriber;</span></li>
<li class="li6"><span class="s1">the Service and all Content are provided &ldquo;as is&rdquo;, and the Province disclaims all representations, warranties, conditions, obligations and liabilities of any kind, whether express or implied, in relation to the Service or any Content, including without limitation implied warranties with respect to merchantability,<span class="Apple-converted-space">&nbsp; </span>fitness for a particular purpose, error-free or uninterrupted use and non-infringement; and</span></li>
<li class="li6"><span class="s1">in no event will the Province, its respective servants, agents, contractors or employees be liable for any loss or damage in connection with the Service or any Content, including without limitation any loss or damage caused by any alteration of the format or content of a print copy or electronic display of any information retrieved from the Service, the quality of any print display, the information contained in any screen dump, any system failure, hardware malfunction, manipulation of data, inadequate or faulty Transaction and/or Service, or delay or failure to provide Access to any User or any person using a User's Incorporation Numbers or Passcodes or using any information provided by a Subscriber or any User from the Service.</span></li>
</ol>
<li class="li6"><span class="s1">The Subscriber must indemnify and save harmless the Province and its respective servants, agents, contractor and employees from any losses, claims, damages, actions, causes of action, costs and expenses that the Province or any of its respective servants, agents, contractors<span class="Apple-converted-space">&nbsp; </span>or employees may sustain, incur, suffer or be put to at any time, either before or after this Agreement ends, including any claim of infringement of third-party intellectual property rights, where the same or any of them are based upon, arise out of or occur, directly or indirectly, by reason of any act or omission by the Subscriber or by any of the Subscriber&rsquo;s agents, employees, officers or directors in connection with this Agreement.&nbsp;</span></li>
</ol>
</ol>
<p class="p13">&nbsp;</p>
<ol class="ol1">
<li class="li8"><span class="s1"><strong>GENERAL</strong></span></li>
</ol>
<p class="p13">&nbsp;</p>
<ol class="ol1">
<ol class="ol1">
<li class="li6"><span class="s1">In this Agreement,</span></li>
<ol class="ol2">
<li class="li6"><span class="s1">unless the context otherwise requires, references to sections by number are to sections of the Agreement;</span></li>
<li class="li6"><span class="s1">unless otherwise specified, a reference to a statute by name means the statute of British Columbia by that name, as amended or replaced from time to time;</span></li>
<li class="li6"><span class="s1"> &ldquo;person&rdquo; includes an individual, partnership, corporation or legal entity of any nature; and</span></li>
<li class="li17"><span class="s1">unless the context otherwise requires, words expressed in the singular includes the plural and <em>vice versa</em>.<span class="Apple-converted-space">&nbsp; </span></span></li>
</ol>
<li class="li6"><span class="s1">This Agreement is the entire agreement between the Subscriber and the Province with respect to the subject matter of this Agreement, and supercedes and replaces any prior and/or written agreements. </span></li>
<li class="li6"><span class="s1">The headings in this Agreement are inserted for convenience only, and will not be used in interpreting or construing any provision of this Agreement.</span></li>
<li class="li6"><span class="s1">All provisions in this Agreement in favour or either party and all rights and remedies of either party, either at law or in equity, will survive the expiration or sooner termination of this Agreement.</span></li>
<li class="li6"><span class="s1">If any provision of this Agreement is invalid, illegal or unenforceable, that provision will be severed from this Agreement and all other provisions will remain in full force and effect.</span></li>
<li class="li6"><span class="s1">This Agreement will be governed by and construed in accordance with the laws of British Columbia and the laws of Canada applicable therein.<span class="Apple-converted-space">&nbsp; </span>By using the Service, the Subcriber consents to the exclusive jurisdiction and venue of the courts of the province of British Columbia for the hearing of any dispute arising from or related to this Agreement and/or the Subscriber&rsquo;s use of the Service.</span></li>
</ol>
</ol>
    """
    op.bulk_insert(
        documents,
        [
            {'version_id': 1, 'type': 'termsofuse', 'content': html_content}
        ]
    )

def downgrade():
    op.drop_constraint('user_documents_fk', 'user', type_='foreignkey')
    op.drop_column('user', 'terms_of_use_accepted_version')
    op.drop_column('user', 'is_terms_of_use_accepted')
    op.drop_table('documents')
