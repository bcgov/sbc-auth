<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
    <h1 class="view-header__title mb-9">
      Getting your identity affidavit notarized
    </h1>
    <p class="mb-9">
      Download the identity affidavit template below and visit a Notary Public or laywer to have it notarized.
    </p>
    </div>
    <p class="mb-4">
      <strong>You will need to bring:</strong>
    </p>
    <div class="mb-9">
      <ol>
        <li>One piece of government-issued photo identification</li>
        <li>A printed copy of the affidavit template</li>
        <li>Payment (most notaries and laywers charge a fee for this service. Fees will vary.)</li>
      </ol>
    </div>
    <p class="mb-10">
      Once you have your affidavit notarized, return to this website and continue to the next step. <span class="lb">You will upload your affidavit later in the account creation process.</span>
    </p>
    <div class="d-inline-flex flex-column pb-2">
      <v-btn
        x-large
        outlined
        depressed
        height="70"
        class="download-btn text-left"
        color="primary"
        @click="downloadAffidavit"
      >
        <v-icon
          x-large
          class="mr-3 ml-n2"
        >
          mdi-file-download-outline
        </v-icon>
        <div>
          <strong>Download Identity Affidavit</strong>
          <div class="file-size mb-1">
            PDF (100KB)
          </div>
        </div>
      </v-btn>
      <v-alert
        dense
        text
        type="error"
        height="42"
        class="mt-3"
        v-if="isDownloadFailed"
      >
        {{downloadFailedMsg}}
      </v-alert>
    </div>
    <v-divider class="my-10"></v-divider>
    <div class="d-flex">
      <v-btn
        large
        depressed
        color="grey lighten-2"
        class="font-weight-bold"
        @click="goBack"
      >
        <v-icon class="mr-2">
          mdi-arrow-left
        </v-icon>
        Back
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        large
        depressed
        color="primary"
        class="font-weight-bold"
        @click="redirectToBceId"
      >
        Next: Register a BCeID
        <v-icon class="ml-2">
          mdi-arrow-right
        </v-icon>
      </v-btn>
    </div>
  </v-container>
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
      CommonUtils.fileDownload(downloadData?.data, `affidavit.pdf`, downloadData?.headers['content-type'])
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      this.isDownloadFailed = true
    }
  }

  private redirectToBceId () {
    window.location.href = ConfigHelper.getBceIdOsdLink()
  }

  private goBack () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE}/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE_INSTRUCTIONS}`)
    window.scrollTo(0, 0)
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    max-width: 60rem;
  }

  .download-btn {
    background: #ffffff;
  }

  .file-size {
    font-size: 0.875rem;
  }

  li {
    padding-left: 0.5rem;
  }

  @media (min-width: 600px) {
    .lb {
      display: block;
    }
  }
</style>
