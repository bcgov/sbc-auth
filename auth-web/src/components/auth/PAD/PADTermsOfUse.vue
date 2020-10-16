<template>
  <div>
    <v-fade-transition>
      <div class="loading-container" v-if="!termsContent">
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="termsContent"
        />
      </div>
    </v-fade-transition>
    <div v-html="termsContent" class="terms-container"></div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
import documentService from '@/services/document.services.ts'

@Component({
  computed: {
    ...mapState('user', ['termsOfUse'])
  },
  methods: {
    ...mapMutations('user', ['setTermsOfUse'])
  }
})
export default class PADTermsOfUse extends Vue {
  private readonly setTermsOfUse!: (terms: TermsOfUseDocument) => void
  private termsContent = ''
  protected readonly userProfile!: User

  @Prop({ default: '' }) private content: string

  async mounted () {
    if (!this.content) {
      const response = await documentService.getTermsOfService('termsofuse')
      if (response.data) {
        this.termsContent = response.data.content
        this.setTermsOfUse(response.data)
        const hasLatestTermsAccepted = this.hasAcceptedLatestTos(
          response.data.versionId
        )
        if (!hasLatestTermsAccepted) {
          this.$emit('update_version')
        }
      }
    } else {
      this.termsContent = this.content
    }
  }

  private hasAcceptedLatestTos (latestVersionId: string) {
    /*
    version id comes with a string prefix like d1 , d2... strip that , convert to number for comparison
    Or else 'd1' will be,l 'd2' . But 'd2' wont be less than ' d10 '!!!  '
    */

    // TODO: check the appropriate field on the account to see if current version has been accepted
    return false
    // if (!this.userProfile.userTerms?.termsOfUseAcceptedVersion) {
    //   return true
    // }
    // const currentlyAcceptedTermsVersion = Number(
    //   // this.userProfile.userTerms.termsOfUseAcceptedVersion.replace(/\D/g, '')
    // )
    // const latestVersionNumber = Number(latestVersionId.replace(/\D/g, ''))

    // return (
    //   this.userProfile.userTerms.isTermsOfUseAccepted &&
    //   currentlyAcceptedTermsVersion > latestVersionNumber
    // )
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Terms and Conditions Container
$indent-width: 3rem;

.terms-container ::v-deep {
  section {
    margin-top: 2rem;
  }

  section header {
    margin-bottom: 1rem;
    color: $gray9;
    letter-spacing: -0.02rem;
    font-size: 1.25rem;
    font-weight: 700;
  }

  section header > span {
    display: inline-block;
    width: $indent-width;
  }

  header + div {
    margin-left: 3.25rem;
  }

  section div > p {
    padding-left: $indent-width;
  }

  p {
    position: relative;
  }

  p + div {
    margin-left: $indent-width;
  }

  p > span {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>
