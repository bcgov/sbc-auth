<template>
  <div>
    <v-fade-transition>
      <div
        v-if="!termsContent"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="termsContent"
        />
      </div>
    </v-fade-transition>
    <div
      class="terms-container"
      v-html="termsContent"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import CommonUtils from '@/util/common-util'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
import { useUserStore } from '@/store/user'

@Component({
  computed: {
    ...mapState(useUserStore, [
      'termsOfUse',
      'userProfile',
      'userHasToAcceptTOS'
    ])
  },
  methods: {
    ...mapActions(useUserStore, [
      'getTermsOfUse'
    ])
  }
})
export default class TermsOfUse extends Vue {
  private readonly getTermsOfUse!: (docType?: string) => TermsOfUseDocument
  private termsContent = ''
  protected readonly userProfile!: User
  protected readonly userHasToAcceptTOS!: boolean

  @Prop({ default: 'termsofuse' }) tosType: string

  async mounted () {
    const termsOfService = await this.getTermsOfUse(this.tosType)
    if (termsOfService) {
      this.termsContent = termsOfService.content
      const hasLatestTermsAccepted = this.hasAcceptedLatestTos(termsOfService?.versionId)
      if (!hasLatestTermsAccepted) {
        this.$emit('tos-version-updated')
      }
    }
  }

  private hasAcceptedLatestTos (latestVersionId: string) {
    /*
    version id comes with a string prefix like d1 , d2... strip that , convert to number for comparison
    Or else 'd1' will be,l 'd2' . But 'd2' wont be less than ' d10 '!!!  '
    */

    const userTOS = this.userProfile?.userTerms?.termsOfUseAcceptedVersion

    if (!userTOS) {
      return true
    }
    const currentlyAcceptedTermsVersion = CommonUtils.extractAndConvertStringToNumber(userTOS)
    const latestVersionNumber = CommonUtils.extractAndConvertStringToNumber(latestVersionId)
    return (currentlyAcceptedTermsVersion > latestVersionNumber)
  }
}
</script>

<style lang="scss" scoped>
  .terms-container {
    ::v-deep {
      section {
        + section {
          margin-top: 2rem;
        }

        header {
          margin-bottom: 1.5rem;
          text-transform: uppercase;
          font-size: 1.125rem;
          font-weight: 700;
        }
      }

      ul {
        list-style-type: none;
        padding-left: 50px !important;
      }

      ul.alpha-listing {
        list-style-type: lower-alpha !important;
      }

      li {
        + li {
          margin-top: 1rem;
        }

        span {
          display: inline-block;
          width: 50px;
          margin-left: -50px;
          font-size: 0.9375rem;
        }
      }
    }
  }
</style>
