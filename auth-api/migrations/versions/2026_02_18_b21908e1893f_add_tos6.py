"""BC Registry and Digital Services Account Agreement ToS version 6

Revision ID: b21908e1893f
Revises: a1b2c3d4e5f6
Create Date: 2026-02-18 13:34:51.142982

"""
from alembic import op
from sqlalchemy import String
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'b21908e1893f'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    documents = table('documents',
                      column('version_id', String),
                      column('type', String),
                      column('content_type', String),
                      column('content', String))

    html_content = """
      <section>
        <p>The parties to these "BC Registry and Digital Services Account Agreement" (the "Agreement") are His Majesty the King in Right of the Province of British Columbia, as represented by the Minister of Citizens' Services (the "Province") and the Subscriber (as defined below).</p>
      </section>
      <section>
        <header>1. <u>DEFINITIONS</u></header>
        <ul>
          <li><span>a)</span><strong>"Access"</strong> means the non-exclusive right to electronically access and use the Service;</li>
          <li><span>b)</span><strong>"Additional Terms"</strong> means, as applicable to the Subscriber's use of the Service, any of the BC Online Terms and Conditions, the BC Services Card Terms, the BCeID Terms, the PAD Agreement, or any combination of the foregoing;</li>
          <li><span>c)</span><strong>"Authenticate" or "Authentication"</strong> means the process of verifying a Subscriber or Team Member's identity for the purpose of obtaining Access, and may include the use of a mobile Services Card, or BCeID Information and an identity affidavit, as applicable;</li>
          <li><span>d)</span><strong>"BCeID Information"</strong> means a BCeID account user ID or password, which authenticates the identity of the Subscriber or a Team Member, as the case may be, to the Service if the Subscriber or a Team Member uses a BCeID for this purpose;</li>
          <li><span>e)</span><strong>"Commencement Date"</strong> means the date on which the Subscriber accepts the terms of this Agreement as part of the application process for Access;</li>
          <li><span>f)</span><strong>"Content"</strong> means the Service's Data Bases, and all associated information and documentation, including any print copy or electronic display of any information retrieved from the Data Base and associated with the Service;</li>
          <li><span>g)</span><strong>"Data Base"</strong> means any data base or information stored in electronic format for which Access is made available through the Service;</li>
          <li><span>h)</span><strong>"Deposit Account"</strong> has the meaning given to it in the BC Online Terms and Conditions;</li>
          <li><span>i)</span><strong>"Entity"</strong> means any legal entity (including a registered society, business, or co-operative) for which certain Subscribers and Team Members may have Access through the Service;</li>
          <li><span>j)</span><strong>"Fees"</strong> means all fees and charges for the Service, as described on the Website, and includes without limitation, any expenses or charges incurred for Transactions, including any applicable Service Fee described in section 8.7 of this Agreement;</li>
          <li><span>k)</span><strong>"Incorporation Number"</strong> means the unique numerical identifier for a Subscriber's Entity, and when entered in conjunction with the Passcode, permits a Team Member to perform transactions with regard to that Entity;</li>
          <li><span>l)</span><strong>"PAD Agreement"</strong> means the agreement referenced in section 8.4;</li>
          <li><span>m)</span><strong>"Passcode"</strong> means the unique identifier issued by the Province to a Subscriber with regard to existing Entities on the Service, which enables a Team Member to have Access with regard to those Entities;</li>
          <li><span>n)</span><strong>"Service"</strong> means all products and services available through BC Registries that may be utilized by Subscriber or any of its Team Members and includes Access, Transactions for such Services, but does not include an API;</li>
          <li><span>o)</span><strong>"Services Card"</strong> means the Subscriber's BC Services Card, which authenticates the identity of the Subscriber, or a Team Member, as the case may be, to the Service if the Subscriber or a Team Member uses a BC Services Card for this purpose;</li>
          <li><span>p)</span><strong>"STRR API"</strong> means the Short-Term Rental Registry API;</li>
          <li><span>q)</span><strong>"Subscriber"</strong> means a person that accesses the Service and that has accepted the terms of this Agreement;</li>
          <li><span>r)</span><strong>"Team Member"</strong> means an individual that is granted Access on the individual's behalf, if the individual is also the Subscriber, or on behalf of the Subscriber, if the individual is an employee or is otherwise authorized to act on behalf of the Subscriber, as applicable;</li>
          <li><span>s)</span><strong>"Transaction"</strong> means any action performed by the Subscriber or any of its Team Members with regard to the Service to display, print, transfer, or obtain a copy of information contained on the Service, where permitted by the Province, to add to or delete information from the Service; or any other action necessary to make use of the Service; and</li>
          <li><span>t)</span><strong>"Website"</strong> means the BC Registry Website at https://www.bcregistry.gov.bc.ca/en-CA and includes all web pages and associated materials, with the exception of the Content.</li>
        </ul>
      </section>
      <section>
        <header>2. <u>ACCEPTANCE OF AGREEMENT</u></header>
        <ul>
          <li><span>2.1</span>The Subscriber acknowledges that a duly authorized representative of the Subscriber has accepted the terms of this Agreement on behalf of the Subscriber and its Team Members.</li>
          <li><span>2.2</span>The Subscriber acknowledges and agrees that:</li>
          <li>
            <ul>
              <li><span>(a)</span>by creating a profile and/or by clicking the button acknowledging acceptance of this Agreement, each Team Member using the Services on behalf of the Subscriber also accepts, and will be conclusively deemed to have accepted, the terms of this Agreement as they pertain to the Team Member's use of the Services;</li>
              <li><span>(b)</span>the Additional Terms are incorporated herein by reference and also govern and apply to the Subscriber and to each Team Member's use of the Service; and</li>
              <li><span>(c)</span>the Subscriber will be solely responsible for its Team Members' use of the Services, including without limitation any Fees incurred by its Team Members in connection with such Services.</li>
            </ul>
          </li>
          <li><span>2.3</span>The Province reserves the right to make changes to the terms of this Agreement at any time without direct notice to either the Subscriber or its Team Members, as applicable. The Subscriber acknowledges and agrees that it is the sole responsibility of the Subscriber to review, and, as applicable, to ensure that its Team Members review, the terms of this Agreement on a regular basis.</li>
          <li><span>2.4</span>Following the date of any such changes, the Subscriber will be conclusively deemed to have accepted any such changes on its own behalf and on behalf of its Team Members, as applicable. The Subscriber acknowledges and agrees that each of its Team Members must also accept any such changes as they pertain to the Team Member's use of the Services.</li>
        </ul>
      </section>
      <section>
        <header>3. <u>AUTHENTICATION</u></header>
        <ul>
          <li><span>3.1</span>Subscribers acknowledge that regardless of the method of Authentication, any information provided as part of the authentication process will be used by the Province in connection with the Services and the Subscriber is responsible for ensuring that such information is up to date and accurate. Subscribers are responsible for ensuring that its Team Members are aware of and will comply with this provision.</li>
          <li><span>3.2</span>If a Subscriber or a Team Member has used the BC Services Card to authenticate in setting up an account to use the Service, the terms found at: <a href="https://id.gov.bc.ca/static/termsOfUse.html" target="_blank">https://id.gov.bc.ca/static/termsOfUse.html</a> (the "BC Services Card Terms") continue to apply in respect of use of the BC Services Card.</li>
          <li><span>3.3</span>If the Subscriber or a Team Member has used a BCeID to authenticate in setting up an account to use the Service, the BCeID terms found at <a href="https://www.bceid.ca/aboutbceid/agreements.aspx" target="_blank">https://www.bceid.ca/aboutbceid/agreements.aspx</a> (the "BCeID Terms") continue to apply in respect of the type of BCEID used.</li>
        </ul>
      </section>
      <section>
        <header>4. <u>PROPRIETARY RIGHTS</u></header>
        <ul>
          <li><span>4.1</span>The Website and the Content is owned by the Province and/or its licensors and is protected by copyright, trademark and other laws. Except as expressly permitted in this Agreement, the Subscriber may not use, reproduce, modify or distribute, or allow any other person to use, reproduce, modify or distribute, any part of the Website in any form whatsoever without the prior written consent of the Province.</li>
        </ul>
      </section>
      <section>
        <header>5. <u>SERVICES</u></header>
        <ul>
          <li><span>5.1</span>The Province will provide the Subscriber and its Team Members with Access on the terms and conditions set out in this Agreement.</li>
          <li><span>5.2</span>Subject to section 5.3, Access will be available during the hours published on the Website, as may be determined by the Province in its sole discretion from time to time.</li>
          <li><span>5.3</span>The Province reserves the right to limit or withdraw Access at any time in order to perform maintenance of the Service or in the event that the integrity or security of the Service is compromised.</li>
          <li><span>5.4</span>The Province further reserves the right to discontinue the Service at any time.</li>
          <li><span>5.5</span>The Province will provide helpdesk support to assist Team Members with Access during the hours published on the Website, as may be determined by the Province in its sole discretion from time to time.</li>
          <li><span>5.6</span>The Subscriber acknowledges and agrees that, for the purpose of Access:</li>
          <li>
            <ul>
              <li><span>(a)</span>it is the Subscriber's sole responsibility, at the Subscriber's own expense, to provide, operate and maintain computer hardware and communications software or web browser software that is compatible with the Services; and</li>
              <li><span>(b)</span>any failure to do so may impact the Subscriber's and/or Team Member's ability to access the Service.</li>
            </ul>
          </li>
        </ul>
      </section>
      <section>
        <header>6. <u>API</u></header>
        <ul>
          <li><span>6.1</span>For greater certainty, the provisions of this Agreement do not apply to the access or use of any API, including the STRR API. Subscribers who have pre-authorized debit as the payment option who wish to access the Content through an API will be required to enter into a separate API Agreement with the Province.</li>
        </ul>
      </section>
      <section>
        <header>7. <u>SUBSCRIBER OBLIGATIONS</u></header>
        <ul>
          <li><span>7.1</span>The Subscriber will comply, and will ensure that all of its Team Members are aware of and will comply, with:</li>
          <li>
            <ul>
              <li><span>(a)</span>the terms of this Agreement, including the requirements regarding the integrity and/or security of the Service set out in this Article 7; and</li>
              <li><span>(b)</span>all applicable laws,</li>
            </ul>
          </li>
          <li>in connection with the Subscriber's and/or Team Members' use of the Services.</li>
          <li><span>7.2</span>The Subscriber will ensure that each Team Member:</li>
          <li>
            <ul>
              <li><span>(a)</span>is duly authorized by the Subscriber to perform any Transaction and utilize the Service on behalf of the Subscriber;</li>
              <li><span>(b)</span>maintains in confidence Services Card Numbers, BCeID Information, Incorporation Numbers and Passcodes;</li>
              <li><span>(c)</span>is competent to perform a Transaction and utilize the Service;</li>
              <li><span>(d)</span>has been adequately trained and instructed to perform a Transaction and utilize the Service; and</li>
              <li><span>(e)</span>does not use the Service for any inappropriate or unlawful purpose.</li>
            </ul>
          </li>
          <li><span>7.3</span>The Subscriber will not, and will ensure that its Team Members do not, take any action that would compromise the integrity and/or security of the Service or any Content.</li>
          <li><span>7.4</span>Without limiting the general nature of the foregoing section, the Subscriber will not, and will ensure that its Team Members do not:</li>
          <li>
            <ul>
              <li><span>(a)</span>use the Service or any Content for activities or for a purpose different from those for which Access was granted;</li>
              <li><span>(b)</span>attempt to circumvent or subvert any security measures;</li>
              <li><span>(c)</span>take any action or use any program that impedes, restricts, limits or otherwise jeopardizes the operation and/or availability of the Service or any Content;</li>
              <li><span>(d)</span>take any action that might reasonably be construed as likely to adversely affect any other Subscriber, or Team Member;</li>
              <li><span>(e)</span>alter or delete any information in any Data Base unless explicitly authorized to do so by the Province;</li>
              <li><span>(f)</span>alter in any way whatsoever a printout or display of any information retrieved from any Data Base unless explicitly authorized to do so by the Province; or</li>
              <li><span>(g)</span>use, reproduce or distribute any altered information, including any printout or display of altered information, or represent any altered information as having been retrieved from any Data Base unless explicitly authorized to do so by the Province.</li>
            </ul>
          </li>
          <li><span>7.5</span>The Subscriber will adhere, and will ensure that each of its Team Members adhere, to any applicable security policies, standards or procedures in respect of a particular Data Base that may be provided to the Subscriber and/or its Team Members by the Province from time to time.</li>
        </ul>
      </section>
      <section>
        <header>8. <u>FEES</u></header>
        <ul>
          <li><span>8.1</span>The Subscriber will pay to the Province all applicable Fees for the Services.</li>
          <li><span>8.2</span>Subject to section 8.5, all Fees are due and payable when a Transaction is processed.</li>
          <li><span>8.3</span>If a Subscriber opts to pay Fees through a Deposit Account, the Fees payable for Transactions will be charged to the applicable Deposit Account and in accordance with the BC Online Terms and Conditions found at <a href="https://www.bconline.gov.bc.ca/terms_conditions.html" target="_blank">(https://www.bconline.gov.bc.ca/terms_conditions.html)</a> (the "BC Online Terms").</li>
          <li><span>8.4</span>If a Subscriber opts to pay Fees through pre-authorized debit, the Fees payable for Transactions will be paid according to the PAD Agreement found at <a href="https://www.bcregistry.ca/business/auth/PAD-terms-and-conditions" target="_blank">(https://www.bcregistry.ca/business/auth/PAD-terms-and-conditions)</a> (the Business Pre-Authorized Debit Terms and Conditions Agreement).</li>
          <li><span>8.5</span>All other Fees payable for Transactions processed by Subscribers will be payable by credit card or online banking before the Transaction is processed.</li>
          <li><span>8.6</span>Unless otherwise specified in this Agreement, all references to money in respect of the Services are to Canadian dollars and all Fees will be processed in Canadian dollars.</li>
          <li><span>8.7</span>The Province may charge the Subscriber a service fee of thirty dollars ($30.00) if any method of payment of any Fees is rejected by the Subscriber's financial institution for any failed payment, and may suspend Access until such service fee and all other Fees owing have been paid by the Subscriber.</li>
          <li><span>8.8</span>By law, some Transactions cannot be reversed and no refund or credit for these types of transactions will be issued. For all other Transactions or Services, any refund or credit is at the sole discretion of the Province.</li>
          <li><span>8.9</span>The Province, by electronic or other means, will provide to a Subscriber, at regular intervals to be determined by the Subscriber from options provided to the Subscriber by the Province, a statement that contains:</li>
          <li>
            <ul>
              <li><span>(a)</span>an itemized list of Transactions and</li>
              <li><span>(b)</span>the total Fees for those Transactions.</li>
            </ul>
          </li>
          <li><span>8.10</span>If a Subscriber has a BC Online account and wishes to receive a statement containing consolidated accounting of Transactions made in BC Online and the new BC Registry System, the Subscriber must link both accounts.</li>
          <li><span>8.11</span>Unless otherwise specified in any Additional Terms, if a Subscriber does not notify the Province in writing of any errors in or objections to any Fees identified in the Statement within ninety (90) days of the date of the applicable invoice, the Fees set out in the invoice will be conclusively deemed to have been accepted as correct by the Subscriber and no claim for adjustment or set-off will be accepted.</li>
        </ul>
      </section>
      <section>
        <header>9. <u>RELATIONSHIP</u></header>
        <ul>
          <li><span>9.1</span>This Agreement will not in any way make the Subscriber or any Team Member an employee, agent or independent contractor of the Province and the Subscriber will not, and will ensure that its Team Members do not, in any way indicate or hold out to any person that the Subscriber or any Team Member is an employee, agent or independent contractor of the Province.</li>
        </ul>
      </section>
      <section>
        <header>10. <u>SUSPENSION OF SERVICE</u></header>
        <ul>
          <li><span>10.1</span>The Province may, in its sole discretion, immediately suspend Access upon notice to the Subscriber in accordance with section 13 if:</li>
          <li>
            <ul>
              <li><span>(a)</span>the Subscriber or any of its Team Members has, in the reasonable opinion of the Province, in any way jeopardized the integrity or security of the Service;</li>
              <li><span>(b)</span>the Subscriber fails to pay Fees in accordance with section 8.2 or 8.5, as applicable; or</li>
              <li><span>(c)</span>the Subscriber or any of its Team Members has violated any other provision of this Agreement.</li>
            </ul>
          </li>
        </ul>
      </section>
      <section>
        <header>11. <u>TERMINATION</u></header>
        <ul>
          <li><span>11.1</span>The term of this Agreement will be from the Commencement Date and will continue until terminated in accordance with the provisions of this Agreement.</li>
          <li><span>11.2</span>The Province may immediately terminate this Agreement upon written notice to the Subscriber if the Subscriber's Access has been suspended pursuant to Article 10.1.</li>
          <li><span>11.3</span>This Agreement may be terminated by either party for any reason upon providing sixty (60) days written notice to the other party.</li>
          <li><span>11.4</span>Upon termination:</li>
          <li>
            <ul>
              <li><span>(a)</span>the Subscriber will immediately cease, and will ensure that all of its Team Members immediately cease, all use on the Subscriber's behalf of the Service and all Passcodes; and</li>
              <li><span>(b)</span>Subscribers will pay to the Province any unpaid Fees incurred by the Subscriber up to the date of termination.</li>
            </ul>
          </li>
          <li><span>11.5</span>In the event that a Subscriber's Agreement is terminated, the Province reserves the right to refuse future Access to that Subscriber.</li>
        </ul>
      </section>
      <section>
        <header>12. <u>WARRANTY DISCLAIMER, LIMITATION OF LIABILITY AND INDEMNITY</u></header>
        <ul>
          <li><span>12.1</span>THE SUBSCRIBER ACKNOWLEDGES AND CONFIRMS THAT THE SUBSCRIBER UNDERSTANDS THAT THIS ARTICLE 12 REQUIRES THE SUBSCRIBER TO ASSUME THE FULL RISK IN RESPECT OF ANY USE OF THE SERVICES BY THE SUBSCRIBER AND/OR ITS TEAM MEMBERS.</li>
          <li><span>12.2</span>Except as expressly set out in this Agreement, and in addition to the Province's general <u>Warranty Disclaimer and Limitation of Liabilities</u>, the Province assumes no responsibility or liability to any person using the Service or any Content. In particular, without limiting the general nature of the foregoing:</li>
          <li>
            <ul>
              <li><span>(a)</span>in no event will the Province, its respective servants, agents, contractors or employees be liable for any direct, indirect, special or consequential damages or other loss, claim or injury, whether foreseeable or unforeseeable (including without limitation claims for damages for personal injury, lost profits, lost savings or business opportunities) arising out of or in any way connected with the use of, or inability to use the Service or any Content;</li>
              <li><span>(b)</span>the entire risk as to the quality and performance of the Service or any Content is assumed by the Subscriber;</li>
              <li><span>(c)</span>the Service and all Content are provided "as is", and the Province disclaims all representations, warranties, conditions, obligations and liabilities of any kind, whether express or implied, in relation to the Service or any Content, including without limitation implied warranties with respect to merchantability, fitness for a particular purpose, error-free or uninterrupted use and non-infringement; and</li>
              <li><span>(d)</span>in no event will the Province, its respective servants, agents, contractors or employees be liable for any loss or damage in connection with the Service or any Content, including without limitation any loss or damage caused by any alteration of the format or content of a print copy or electronic display of any information retrieved from the Service, the quality of any print display, the information contained in any screen dump, any system failure, hardware malfunction, manipulation of data, inadequate or faulty Transaction and/or Service, or delay or failure to provide Access to any Team Member or any person using a Team Member's Incorporation Numbers or Passcodes or using any information provided by a Subscriber or any Team Member from the Service.</li>
            </ul>
          </li>

          <li><span>12.3</span>The Subscriber must indemnify and save harmless the Province and its respective servants, agents, contractor and employees from any losses, claims, damages, actions, causes of action, costs and expenses that the Province or any of its respective servants, agents, contractors or employees may sustain, incur, suffer or be put to at any time, either before or after this Agreement ends, including any claim of infringement of third-party intellectual property rights, where the same or any of them are based upon, arise out of or occur, directly or indirectly, by reason of any act or omission by the Subscriber, a Team Member or by any of the Subscriber's other agents, employees, officers or directors in connection with this Agreement.</li>
        </ul>
      </section>
      <section>
        <header>13. <u>NOTICES</u></header>
        <ul>
          <li><span>13.1</span>Any written notice either party may be required or may desire to give to the other under this Agreement will be conclusively deemed validly given to or received by the addressee, if delivered personally or by recognized courier service, on the date of such personal delivery, if mailed by prepaid registered mail, on the third business day after the mailing of the same in British Columbia or on the seventh business day if mailed elsewhere, and if delivered by email, on the date received by the recipient:</li>
          <li>
            <ul>
              <li><span>(a)</span>If to the Subscriber, to the address or email address indicated on the Subscriber's application for the Service, or such other address or email address of which the Subscriber has notified the Province in writing; and</li>
              <li><span>(b)</span>If to the Province:</li>
            </ul>
          </li>
          <li>
            <p>Delivery by mail:</p>
            <p>BC OnLine Partnership Office<br>Ministry of Citizens' Services<br>PO Box 9412 Stn Prov Govt<br>Victoria, BC V8W 9V1</p>
            <p>Delivery by courier or in person:</p>
            <p>BC OnLine Partnership Office<br>Ministry of Citizens' Services<br>E161 – 4000 Seymour Place<br>Victoria, BC V8X 4S8</p>
            <p>Delivery by email:</p>
            <p>bconline@gov.bc.ca</p>
          </li>
          <li><span>13.2</span>The Subscriber will provide the Province with timely written notice of any change of contact information provided by the Subscriber during the application process for Access, and after the provision of such notice, the updated contact information will be conclusively deemed to be the current contact information for the Subscriber, including the Subscriber's address or email address for the purposes of this Article 13.</li>
          <li><span>13.3</span>The Province may, from time to time, advise the Subscriber by notice in writing of any change of address of the Province and from and after the giving of such notice the address specified in the notice will, for the purposes of this Article 13, be conclusively deemed to be the address or email address of the Province.</li>
          <li><span>13.4</span>In the event of a disruption of postal services, all mailed notices will be deemed validly given and received when actually received by the addressee.</li>
        </ul>
      </section>
      <section>
        <header>14. <u>GENERAL</u></header>
        <ul>
          <li><span>14.1</span>In this Agreement,</li>
          <li>
            <ul>
              <li><span>(a)</span>unless the context otherwise requires, references to section or Articles by number are to sections or Articles of the body of the Agreement;</li>
              <li><span>(b)</span>unless otherwise specified, a reference to a statute by name means the statute of British Columbia by that name, as amended or replaced from time to time;</li>
              <li><span>(c)</span>"person" includes an individual, partnership, corporation or legal entity of any nature; and</li>
              <li><span>(d)</span>unless the context otherwise requires, words expressed in the singular includes the plural and vice versa.</li>
            </ul>
          </li>
          <li><span>14.2</span>The Subscriber will not, without the prior written consent of the Province, assign, either directly or indirectly, this Agreement or any right of the Subscriber under this Agreement.</li>
          <li><span>14.3</span>This Agreement will be for the benefit of and be binding upon the successors and permitted assigns of each of the parties.</li>
          <li><span>14.4</span>This Agreement (including any terms incorporated by reference herein) is the entire agreement between the Subscriber and the Province with respect to the subject matter of this Agreement, and supercedes and replaces any prior and/or written agreements.</li>
          <li><span>14.5</span>The headings in this Agreement are inserted for convenience only, and will not be used in interpreting or construing any provision of this Agreement.</li>
          <li><span>14.6</span>All provisions in this Agreement in favour or either party and all rights and remedies of either party, either at law or in equity, will survive the expiration or sooner termination of this Agreement.</li>
          <li><span>14.7</span>If any provision of this Agreement is invalid, illegal or unenforceable, that provision will be severed from this Agreement and all other provisions will remain in full force and effect.</li>
          <li><span>14.8</span>This Agreement will be governed by and construed in accordance with the laws of British Columbia and the laws of Canada applicable therein. By using the Service, the Subscriber consents to the exclusive jurisdiction and venue of the courts of the province of British Columbia for the hearing of any dispute arising from or related to this Agreement and/or the Subscriber's use of the Service.</li>
        </ul>
      </section>
    """

    op.bulk_insert(
        documents,
        [
            {'version_id': '6', 'type': 'termsofuse', 'content': html_content, 'content_type': 'text/html'}
        ]
    )


def downgrade():
    op.execute("DELETE FROM DOCUMENTS WHERE version_id='6' AND type='termsofuse'")
