"""add term of use for director search

Revision ID: 08063ceec05d
Revises: 22e86ed493b8
Create Date: 2020-05-01 10:29:53.862248

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy import Integer, String

# revision identifiers, used by Alembic.
revision = '08063ceec05d'
down_revision = '22e86ed493b8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('user_documents_fk', 'user', type_='foreignkey')
    op.alter_column('user', 'terms_of_use_accepted_version', existing_type=Integer, type_=sa.String(length=10))
    op.alter_column('documents', 'version_id', existing_type=Integer, type_=sa.String(length=10))
    op.alter_column('documents', 'type', existing_type=sa.String(length=20), type_=sa.String(length=30))
    op.create_foreign_key('user_documents_fk', 'user', 'documents', ['terms_of_use_accepted_version'], ['version_id'])

    documents = table('documents',
                      column('version_id', String),
                      column('type', String),
                      column('content', String))

    html_content = """
    <article>
        <p>The Director Search Tool provides access to investigative agencies looking to perform searches related to registered BC Companies.</p>
        <p>These Terms of Use (the “Terms”) set out the terms and conditions that govern the access and use of investigative agencies (each an “Agency”) of the Director Search Tool operated by Her Majesty the Queen in Right of the Province of British Columbia, represented by the Minister of Citizens’ Services (the “Province”) (the “Tool”). In order to use the Tool, it is necessary for a representative of an Agency to complete a request for access to the Tool and accept the related terms of that access request. Signing the access request for the Tool and acceptance of the Terms constitutes unconditional acceptance by the Agency of the Terms.    <em><u></u></em></p>
        <section>
            <div>
                <p><em><u></u></em></p>

                <section>
                    <div>
                        <span><em><u>Authority and Ability to Accept Terms</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>1.</span>The individual accepting these Terms on behalf of an Agency represents and warrants that</p>
                        <div>
                            <p><span>a.</span>s/he is at least 19 years of age; and</p>
                            <p><span>b.</span>s/he has all necessary authority to accept these Terms on behalf of the Agency and, where the Agency is not a separate legal entity from the individual, on his/her own behalf, in which case references in these Terms to the “Agency” include the individual accepting these Terms.</p>
                        </div>
                    </div>
                </section>
                <section>
                    <div>
                        <span><em><u>Responsibility for Users</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>2.</span>The Agency acknowledges and agrees that it is responsible for ensuring that any of its employees, agents and representatives (collectively, “<strong>Users</strong>”) who access or use the Tool comply with these Terms.</p>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Acceptable Use</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>3.</span>The Agency must not use the Tool in any way that would jeopardize the security, integrity and/or availability of the Tool. Without limiting the general nature of the foregoing sentence, the Agency must not:</p>
                        <div>
                            <p><span>(a)</span>use the Tool for any unlawful or inappropriate purpose;</p>
                            <p><span>(b)</span>tamper with any portion of the Tool;</p>
                            <p><span>(c)</span>input or upload to the Tool any information which contains viruses, Trojan horses, worms, time bombs or other computer programming routines that may damage or interfere with the performance or function of the Tool;</p>
                            <p><span>(d)</span>use the Tool to conduct hacking/intrusion activities;</p>
                            <p><span>(e)</span>attempt to circumvent or subvert any security measure associated with the Tool;</p>
                            <p><span>(f)</span>take any action that might reasonably be construed as likely to adversely affect other users of the Tool; or</p>
                            <p><span>(g)</span>remove or alter any proprietary symbol or notice, including any copyright notice, trade-mark or logo displayed in connection with the Tool.</p>
                        </div>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Acceptance of Terms</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>4.</span>By clicking the “Accept” button (or any similar button or mechanism) and accessing and/or using the Tool, the Agency is conclusively deemed to have read and agreed unconditionally to these Terms of Use. If the Agency does not agree with any provision of these Terms of Use, the Agency must close the browser and must not access or use the Tool.</p>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Limitation of Liability and Indemnity</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>5.</span>The Agency agrees that under no circumstances will the Province be liable to the Agency or to any other individual or entity for any direct, indirect, special, incidental, consequential or other loss, claim, injury, or damage, whether foreseeable or unforeseeable (including without limitation claims for damages for loss of profits or business opportunities, use of or inability to use the Tool, interruptions, deletion or corruption of files, loss of programs or information, errors, defects or delays) arising out of or in any way connected with the Agency’s access or use of the Tool or any failure by the Agency to abide by these Terms of Use and whether based on contract, tort, strict liability or any other legal theory. The previous sentence will apply even if the Province have been specifically advised of the possibility of any such loss, claim, injury, or damage.</p>
                        <p><span>6.</span>The Agency agrees to indemnify, defend and hold harmless the Province and the Province’ employees and agents from and against all claims, demands, obligations, losses, liabilities, costs or debt, and expenses (including but not limited to reasonable legal fees) arising from:</p>
                        <div>
                            <p><span>(a)</span>use of the Tool; or</p>
                            <p><span>(b)</span>violation of any provision of these Terms of Use.</p>
                        </div>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Disclaimer:</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>7.</span>The Tool is provided “as is” without warranty of any kind, whether express or implied. All implied warranties, including, without limitation, implied warranties of merchantability, fitness for purpose, and non-infringement are hereby expressly disclaimed. The Agency’s use of the Tool is entirely at the Agency’s own risk and the Agency will be liable for any failure to abide by these Terms of Use. The Province make no representations or warranties, expressed or implied, that:</p>
                        <div>
                            <p><span>(a)</span>the Tool will be available or the Agency’s use of the Tool will be timely, uninterrupted or error free;</p>
                            <p><span>(b)</span>the information on the Tool is accurate, complete or current; or</p>
                            <p><span>(c)</span>the Tool will meet the Agency’s expectations and requirements.</p>
                        </div>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Termination of Tool and Amendment to Terms:</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>8.</span>The Province reserve the right, at any time, to:</p>
                        <div>
                            <p><span>(a)</span>make changes to the Tool;</p>
                            <p><span>(b)</span>stop providing the Tool; and</p>
                            <p><span>(c)</span>modify these Terms of Use at any time, without notice being provided directly to the Agency.</p>
                        </div>
                        <p><em><u></u></em></p>
                        <p><span>9.</span>It is the Agency’s responsibility to review the Terms of Use on a regular basis to ensure that the Agency is aware of any modifications that may have been made. The Agency’s continued use of the Tool constitutes the Agency’s acceptance of any such modified Terms of Use. In the event that the Agency does not agree to be bound by such modified Terms of Use, then the Agency’s sole remedy is to stop using the Tool.</p>
                        <p><span>10.</span>The Agency’s right to use the Tool will terminate automatically:</p>
                        <div>
                            <p><span>(a)</span>if the Province decide to stop providing the Tool, in their sole discretion, for any reason; or</p>
                            <p><span>(b)</span>if the Agency fails to comply with any provision of these Terms of Use,</p>
                        </div>
                        <p>and upon termination, the Agency must immediately cease all use of the Tool.</p>
                    </div>
                </section>

                <section>
                    <div>
                        <span><em><u>Additional Terms:</u></em></span>
                    </div>
                    <p><em><u></u></em></p>
                    <div>
                        <p><span>11.</span>If any term or provision of these Terms of Use is invalid, illegal or unenforceable, all other terms and provisions of these Terms of Use will nonetheless remain in full force and effect.</p>
                        <p><span>12.</span>These Terms of Use will be governed by and construed in accordance with the laws of British Columbia and the laws of Canada applicable in British Columbia.</p>
                        <p><span>13.</span>The Agency agrees that any action at law or in equity in any way arising from the Terms of Use and/or in any way associated with the Agency’s use of the Tool will be resolved by arbitration under the <em>Arbitration Act</em> (British Columbia) and that the place of arbitration will be Victoria, British Columbia.</p>
                        <p><span>14.</span>These Terms of Use (and any terms specifically referred to in these Terms of Use) constitute the entire agreement between the Agency and the Province with respect to the Agency’s use of the Tool.</p>
                    </div>
                </section>

            </div>
        </section>
</article>
    """

    op.bulk_insert(
        documents,
        [
            {'version_id': 'd1', 'type': 'termsofuse_directorsearch', 'content': html_content}
        ]
    )


def downgrade():
    op.execute('DELETE DOCUMENTS WHERE version_id="d1" AND type="termsofuse_directorsearch"')
    op.drop_constraint('user_documents_fk', 'user', type_='foreignkey')
    op.alter_column('documents', 'type', existing_type=sa.String(length=30), type_=sa.String(length=20))
    op.alter_column('documents', 'version_id', existing_type=sa.String(length=2), type_=Integer)
    op.alter_column('user', 'terms_of_use_accepted_version', existing_type=sa.String(length=2), type_=Integer)
    op.create_foreign_key('user_documents_fk', 'user', 'documents', ['terms_of_use_accepted_version'], ['version_id'])
