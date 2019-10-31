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

    html_content = """
    <article>
    <p>The parties to this “Cooperatives Registry Terms and Conditions of Agreement” (the <strong>“Agreement”</strong>) are Her Majesty the Queen in Right of the Province of British Columbia, as represented by the Minister of Citizens’ Services (the <strong>“Province”</strong>) and the Subscriber (as defined below).</p>

    <section>
      <header><span>1.</span> Definitions</header>
      <div>
        <p><span>a.</span>&nbsp;<strong>“Access”</strong> means the non-exclusive right to electronically access and use the Service;</p>
        <p><span>b.</span>&nbsp;<strong>“Basic Account Subscriber”</strong> means a Subscriber with Access to up to ten Entities that pays Fees for Transactions using a credit card;</p>
        <p><span>c.</span>&nbsp;<strong>“BC Online Terms and Conditions”</strong> means the BC Online Terms and Conditions of Agreement found at <a href="https://www.bconline.gov.bc.ca/terms_conditions.html">https://www.bconline.gov.bc.ca/terms_conditions.html</a></p>
        <p><span>d.</span>&nbsp;<strong>"Content"</strong> means the Service’s Data Base, and all associated information and documentation, including any print copy or electronic display of any information retrieved from the Data Base and associated with the Service;</p>
        <p><span>e.</span>&nbsp;<strong>"Data Base"</strong> means any data base or information stored in electronic format for which Access is made available through the Service;</p>
        <p><span>f.</span>&nbsp;<strong>"Deposit Account"</strong> has the meaning given to it in the BC Online Terms and Conditions;</p>
        <p><span>g.</span>&nbsp;<strong>"Entity"</strong> means any BC co-operative for which a User has Access through the Service;</p>
        <p><span>h.</span>&nbsp;<strong>"Fees"</strong> <em>means all fees and charges for the Service, as described in the Business Corporations Act - Schedule (Section 431) Fees, Cooperative Association Act - Cooperative Association Regulation, Schedule A;</em></p>
        <p><span>i.</span>&nbsp;<strong>"Incorporation Number"</strong> means the unique numerical identifier for a Subscriber’s cooperative association, and when entered in conjunction with the Passcode, permits a User to access the Service;</p>
        <p><span>j.</span>&nbsp;<strong>"Passcode"</strong> means the unique identifier issued by the Province to a Subscriber with regard to an Entity, which enables a User to have Access with regard to that Entity within the Service;</p>
        <p><span>k.</span>&nbsp;<strong>"Premium Account Subscriber"</strong> means a Subscriber with Access to unlimited Entities that has a Deposit Account with the Province and is charged Fees in accordance with the BC Online Terms and Conditions;</p>
        <p><span>l.</span>&nbsp;<strong>"Service"</strong> means the service operated by the Province that allows a Subscriber to completeTransactions relating to BC Entities.</p>
        <p><span>m.</span>&nbsp;<strong>"Services Card Number"</strong> means the User’s BC Services Card number, which authenticates the identity of the User to the Service; </p>
        <p><span>n.</span>&nbsp;<strong>"Subscriber"</strong> means a person that accesses the Service and that has accepted the terms of this Agreement, and includes Premium Account Subscribers and Basic Account Subscribers;</p>
        <p><span>o.</span>&nbsp;<strong>"Transaction"</strong> means any action performed by the Subscriber or any of its Users to the Service to display, print, transfer, or obtain a copy of information contained on the Service, or where permitted by the Province, to add to or delete information from the Service.</p>
        <p><span>p.</span>&nbsp;<strong>"User"</strong> means an individual that is granted Access on the individual’s behalf, if the individual is also the Subscriber, or on behalf of the Subscriber, if the individual is an employee or is otherwise authorized to act on behalf of the Subscriber, as applicable;</p>
        <p><span>q.</span>&nbsp;<strong>"Website"</strong> means the BC Cooperatives Website at bcregistry.ca/cooperatives         and includes all web pages and associated materials, with the exception of the Content.</p>
      </div>
    </section>

    <section>
      <header><span>2.</span> Acceptance of Agreement</header>
      <div>
        <p><span>1.1</span>The Subscriber acknowledges that a duly authorized representative of the Subscriber has accepted the terms of this Agreement on behalf of the Subscriber and its Users.</p>
        <p><span>1.2</span>The Subscriber acknowledges and agrees that:</p>
        <div>
          <p><span>(a)</span> by creating a profile and/or by clicking the button acknowledging acceptance of this Agreement, each User using the Services on behalf of the Subscriber also accepts, and will be conclusively deemed to have accepted, the terms of this Agreement as they pertain to the User’s use of the Services; and</p>
          <p><span>(b)</span>the Subscriber will be solely responsible for its Users’ use of the Services, including without limitation any Fees incurred by its Users in connection with such Services.</p>
        </div>
        <p><span>1.3</span>The Subscriber acknowledges that the terms of the BC Services Card Login Service found at (<a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/terms-of-use" target="_blank">https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/terms-of-use</a>) continue to apply in respect of use of the Services Card.</p>
        <p><span>1.4</span>Premium Account Subscribers acknowledge that in addition to this Agreement, the terms of the BC Online Terms and Conditions will continue to apply in respect of the use of the Subscriber’s Deposit Account for payment of Fees for the Service.</p>
        <p><span>1.5</span>The Subscriber will ensure that each of its Users are aware of and comply with the terms of this Agreement as they pertain to the User’s use of the Services.</p>
        <p><span>1.6</span>The Province reserves the right to make changes to the terms of this Agreement at any time without direct notice to either the Subscriber or its Users, as applicable. The Subscriber acknowledges and agrees that it is the sole responsibility of the Subscriber to review, and, as applicable, to ensure that its Users review, the terms of this Agreement on a regular basis.</p>
        <p><span>1.7</span>Following the date of any such changes, the Subscriber will be conclusively deemed to have accepted any such changes on its own behalf and on behalf of its Users, as applicable.  The Subscriber acknowledges and agrees that each of its Users must also accept any such changes as they pertain to the User’s use of the Services.</p>
      </div>
    </section>

    <section>
      <header><span>2.</span> PROPRIETARY RIGHTS</header>
      <div>
        <p><span>2.1</span>The Website and the Content is owned by the Province and/or its licensors and is protected by copyright, trademark and other laws.  Except as expressly permitted in this Agreement, the Subscriber may not use, reproduce, modify or distribute, or allow any other person to use, reproduce, modify or distribute, any part of the Website in any form whatsoever without the prior written consent of the Province. </p>
      </div>
    </section>

    <section>
      <header><span>3.</span> SERVICES</header>
      <div>
        <p><span>3.1</span>The Province will provide the Subscriber and its Users with Access on the terms and conditions set out in this Agreement.</p>
        <p><span>3.2</span>Subject to section 3.3, Access will be available during the hours published on the Website, as may be determined by the Province in its sole discretion from time to time.</p>
        <p><span>3.3</span>The Province reserves the right to limit or withdraw Access at any time in order to perform maintenance of the Service or in the event that the integrity or security of the Service is compromised.</p>
        <p><span>3.4</span>The Province further reserves the right to discontinue the Service at any time.</p>
        <p><span>3.5</span>The Province will provide helpdesk support to assist Users with Access during the hours published on the Website, as may be determined by the Province in its sole discretion from time to time.</p>
        <p><span>3.6</span>The Subscriber acknowledges and agrees that, for the purpose of Access:</p>
        <div>
          <p><span>(a)</span>it is the Subscriber’s sole responsibility, at the Subscriber’s own expense, to provide, operate and maintain computer hardware and communications software or web browser software that is compatible with the Services; and</p>
          <p><span>(b)</span>that any failure to do so may impact the Subscriber’s and/or User’s ability to access the Service.</p>
        </div>
      </div>
    </section>

    <section>
      <header><span>4.</span> SUBSCRIBER OBLIGATIONS</header>
      <div>
        <p><span>4.1</span>The Subscriber will comply, and will ensure that all of its Users comply, with:</p>
        <div>
          <p><span>(a)</span>the requirements regarding the integrity and/or security of the Service set out in this Article 4; and</p>
          <p><span>(b)</span>all applicable laws</p>
        </div>
        <p>in connection with the Subscriber’s and/or Users’ use of the Services.  </p>
        <p><span>4.2</span>The Subscriber will ensure that each User:</p>
        <div>
          <p><span>(a)</span>is duly authorized by the Subscriber to perform any Transaction and utilize the Service on behalf of the Subscriber;</p>
          <p><span>(b)</span>maintains in confidence Services Card Numbers, Incorporation Numbers and Passcodes;</p>
          <p><span>(c)</span>is competent to perform a Transaction and utilize the Service; </p>
          <p><span>(d)</span>has been adequately trained and instructed to perform a Transaction and utilize the Service; and</p>
          <p><span>(e)</span>does not use the Service for any inappropriate or unlawful purpose.</p>
        </div>
      </div>
    </section>

    <section>
      <header><span>5.</span> FEES</header>
      <div>
        <p><span>5.1</span>The Subscriber will pay to the Province all applicable Fees for the Services.</p>
        <p><span>5.2</span>Fees payable for Transactions processed by Premium Account Subscribers will be charged to the applicable Deposit Account and in accordance with the BC Online Terms and Conditions.</p>
        <p><span>5.3</span>Fees payable for Transactions processed by Basic Account Subscribers will be payable by credit card before the Transaction is processed.</p>
      </div>
    </section>

    <section>
      <header><span>6.</span> RELATIONSHIP</header>
      <div>
        <p><span>6.1</span>This Agreement will not in any way make the Subscriber or any User an employee, agent or independent contractor of the Province and the Subscriber will not, and will ensure that its Users do not, in any way indicate or hold out to any person that the Subscriber or any User is an employee, agent or independent contractor of the Province.</p>
      </div>
    </section>

    <section>
      <header><span>7.</span> SUSPENSION OF SERVICE </header>
      <div>
        <p><span>7.1</span>The Province may, in its sole discretion, immediately suspend Access upon written notice to the Subscriber if:</p>
        <div>
          <p><span>(a)</span>the Subscriber or any of its Users has, in the reasonable opinion of the Province, in any way jeopardized the integrity or security of the Service; or</p>
          <p><span>(b)</span>the Subscriber or any of its Users has violated any other provision of this Agreement.</p>
        </div>
      </div>
    </section>

    <section>
      <header><span>8.</span> TERMINATION</header>
      <div>
        <p><span>8.1</span>The Province may immediately terminate this Agreement upon written notice to the Subscriber if the Subscriber’s Access has been suspended pursuant to section 7.1.</p>
        <p><span>8.2</span>Upon termination:</p>
        <div>
          <p><span>(a)</span>the Subscriber will immediately cease, and will ensure that all of its Users immediately cease, all use of the Service and all Passcodes; and</p>
          <p><span>(b)</span>Premium Account Subscribers will pay to the Province all unpaid Fees incurred by the Subscriber up to the date of termination.</p>
        </div>
        <p><span>8.3</span>In the event that a Subscriber’s Agreement is terminated, the Province reserves the right to refuse future Access to that Subscriber or to downgrade a Premium Account Subscriber to a Basic Account Subscriber, in which case the Subscriber acknowledges and agrees that it is only entitled to Access up to ten Entities and will release any Entities in excess of that number.</p>
      </div>
    </section>

    <section>
      <header>9. WARRANTY DISCLAIMER, LIMITATION OF LIABILITY AND INDEMNITY</header>
      <div>
        <p><span>9.1</span>THE SUBSCRIBER  ACKNOWLEDGES AND CONFIRMS THAT THE SUBSCRIBER UNDERSTANDS THAT THIS ARTICLE 10 REQUIRES THE SUBSCRIBER TO ASSUME THE FULL RISK IN RESPECT OF ANY USE OF THE SERVICES BY THE SUBSCRIBER AND/OR ITS USERS</p>
        <p><span>9.2</span>Except as expressly set out in this Agreement, and in addition to the Province’s general <a href="https://www2.gov.bc.ca/gov/content/home/disclaimer" target="_blank">Warranty Disclaimer and Limitation of Liabilities</a>, the Province assumes no responsibility or liability to any person using the Service or any Content. In particular, without limiting the general nature of the foregoing:</p>
        <div>
          <p><span>(a)</span>in no event will the Province, its respective servants, agents, contractors or employees be liable for any direct, indirect, special or consequential damages or other loss, claim or injury, whether foreseeable or unforeseeable (including without limitation claims for damages for personal injury, lost profits, lost savings or business opportunities) arising out of or in any way connected with the use of, or inability to use the Service or any Content;</p>
          <p><span>(b)</span>the entire risk as to the quality and performance of the Service or any Content, is assumed by the Subscriber;</p>
          <p><span>(c)</span>the Service and all Content are provided “as is”, and the Province disclaims all representations, warranties, conditions, obligations and liabilities of any kind, whether express or implied, in relation to the Service or any Content, including without limitation implied warranties with respect to merchantability,  fitness for a particular purpose, error-free or uninterrupted use and non-infringement; and</p>
          <p><span>(d)</span>in no event will the Province, its respective servants, agents, contractors or employees be liable for any loss or damage in connection with the Service or any Content, including without limitation any loss or damage caused by any alteration of the format or content of a print copy or electronic display of any information retrieved from the Service, the quality of any print display, the information contained in any screen dump, any system failure, hardware malfunction, manipulation of data, inadequate or faulty Transaction and/or Service, or delay or failure to provide Access to any User or any person using a User's Incorporation Numbers or Passcodes or using any information provided by a Subscriber or any User from the Service.</p>
        </div>
        <p><span>9.3</span>The Subscriber must indemnify and save harmless the Province and its respective servants, agents, contractor and employees from any losses, claims, damages, actions, causes of action, costs and expenses that the Province or any of its respective servants, agents, contractors or employees may sustain, incur, suffer or be put to at any time, either before or after this Agreement ends, including any claim of infringement of third-party intellectual property rights, where the same or any of them are based upon, arise out of or occur, directly or indirectly, by reason of any act or omission by the Subscriber or by any of the Subscriber’s agents, employees, officers or directors in connection with this Agreement.</p>
      </div>
    </section>

    <section>
      <header>10. GENERAL</header>
      <div>
        <p><span>10.1</span>In this Agreement,</p>
        <div>
          <p><span>(a)</span>unless the context otherwise requires, references to sections by number are to sections of the Agreement;</p>
          <p><span>(b)</span>unless otherwise specified, a reference to a statute by name means the statute of British Columbia by that name, as amended or replaced from time to time;</p>
          <p><span>(c)</span>“person” includes an individual, partnership, corporation or legal entity of any nature; and</p>
          <p><span>(d)</span>unless the context otherwise requires, words expressed in the singular includes the plural and vice versa.</p>
        </div>
        <p><span>10.2</span>This Agreement is the entire agreement between the Subscriber and the Province with respect to the subject matter of this Agreement, and supercedes and replaces any prior and/or written agreements.</p>
        <p><span>10.3</span>The headings in this Agreement are inserted for convenience only, and will not be used in interpreting or construing any provision of this Agreement.</p>
        <p><span>10.4</span>All provisions in this Agreement in favour or either party and all rights and remedies of either party, either at law or in equity, will survive the expiration or sooner termination of this Agreement.</p>
        <p><span>10.5</span>If any provision of this Agreement is invalid, illegal or unenforceable, that provision will be severed from this Agreement and all other provisions will remain in full force and effect.</p>
        <p><span>10.6</span>This Agreement will be governed by and construed in accordance with the laws of British Columbia and the laws of Canada applicable therein.  By using the Service, the Subcriber consents to the exclusive jurisdiction and venue of the courts of the province of British Columbia for the hearing of any dispute arising from or related to this Agreement and/or the Subscriber’s use of the Service.</p>
      </div>
    </section>

  </article>
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
