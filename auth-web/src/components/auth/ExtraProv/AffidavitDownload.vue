<template>
  <div class="d-flex justify-center pa-4">
    <div class="non-bc-instructions-container">
      <v-alert
              dense
              outlined
              type="error"
              v-if="isDownloadFailed"
      >
        {{downloadFailedMsg}}
      </v-alert>
      <h1 class="my-5">
        Getting your identity affidavit notarized
      </h1>
      <p class="mb-5 mt-7">
        Download the identity affidavit template below and visit a Notary Public or laywer to have it notarized.
      </p>
      <div class="mb-5 font-weight-bold">
        You will need to bring:
      </div>
      <div class="mb-5">
        <ol>
          <li>One piece of government-issued photo identification</li>
          <li>A printed copy of the affidavit template</li>
          <li>Payment (most notaries and laywers charge a fee for this service. Fees will vary.)</li>
        </ol>
      </div>
      <p class="mb-10">
        Once you have your affidavit notarized, return to this website and continue to the next step. You will upload your affidavit later in the account creation process
      </p>
      <div class="pb-2">
        <v-btn
          depressed
          outlined
          x-large
          height="70"
          class="download-affidavit-btn"
          color="primary"
          @click="downloadAffidavit"
        >
          <v-icon
            x-large
            class="mr-2"
          >
            mdi-file-pdf-outline
          </v-icon>
          <div>
            <div>Download Identity Affidavit</div>
            <div class="caption font-weight-bold text-left">
              PDF(100KB)
            </div>
          </div>
        </v-btn>
      </div>
      <v-divider class="my-10"></v-divider>
      <div class="d-flex mb-6">
        <v-btn
          class="font-weight-bold"
          color="grey lighten-2"
          depressed
          large
          @click="goBack"
        >
          <v-icon class="mr-2">
            mdi-arrow-left
          </v-icon>
          Back
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          class="font-weight-bold"
          color="primary"
          depressed
          large
          @click="redirectToBceId"
        >
          Continue: Register a BCeID
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import DocumentService from '@/services/document.services'
import { Pages } from '@/util/constants'

@Component
export default class AffidavitDownload extends Vue {
  private downloadFailedMsg = 'Failed download'
  private isDownloadFailed = false

  private async downloadAffidavit () {
    try {
      this.isDownloadFailed = false
      const downloadData = await DocumentService.getAffidavitPdf()
      CommonUtils.fileDownload(downloadData, `affidavit.pdf`)
    } catch (e) {
      this.isDownloadFailed = true
    }
  }

  private redirectToBceId () {
    window.location.href = ConfigHelper.getBceIdOsdLink()
  }

  private goBack () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE}/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE_INSTRUCTIONS}`)
  }
}
</script>

<style lang="scss" scoped>
.non-bc-instructions-container {
  max-width: 660px;
}
.download-affidavit-btn {
  font-weight: 600;
  background: #fff;
}
</style>
