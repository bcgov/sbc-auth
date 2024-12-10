import CommonUtils from '@/util/common-util'
import PaymentService from '@/services/payment.services'
import { StatementListItem } from '@/models/statement'
import { PayDocumentTypes } from '@/util/constants'

export function useDownloader (orgStore, state) {
  async function downloadStatement (statement: StatementListItem) {
    try {
      state.loading = true
      const fileType = 'application/pdf'
      const response = await orgStore.getStatement({ statementId: statement.id, type: fileType })
      const contentDispArr = response?.headers['content-disposition'].split('=')
      const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-statement-pdf`
      CommonUtils.fileDownload(response.data, fileName, 'application/pdf')
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
    } finally {
      state.loading = false
    }
  }

  async function downloadEFTInstructions () {
    state.isLoading = true
    try {
      const downloadData = await PaymentService.getDocument(PayDocumentTypes.EFT_INSTRUCTIONS)
      CommonUtils.fileDownload(downloadData?.data, `bcrs_eft_instructions.pdf`, downloadData?.headers['content-type'])
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
    } finally {
      state.isLoading = false
    }
  }
  return {
    downloadEFTInstructions,
    downloadStatement
  }
}
