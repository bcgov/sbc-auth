<template>
  <div>
    <v-alert
      icon="mdi-information-outline"
      prominent
      text
      type="info"
      v-if="updatedWarning"
    >
      {{ updatedWarning }}
    </v-alert>
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
    ...mapState('user', ['termsOfUse', 'userProfile'])
  },
  methods: {
    ...mapMutations('user', ['setTermsOfUse'])
  }
})
export default class TermsOfUse extends Vue {
  private readonly setTermsOfUse!: (terms: TermsOfUseDocument) => void
  private termsContent = ''
  private updatedWarning = ''
  protected readonly userProfile!: User

  @Prop({ default: '' }) private content: string

  async mounted () {
    if (!this.content) {
      const response = await documentService.getTermsOfService('termsofuse')
      if (response.data) {
        this.termsContent = response.data.content
        this.setTermsOfUse(response.data)
        const hasLatestTermsAccepted = this.hasAcceptedLatestTos(
          response.data.version_id
        )
        if (!hasLatestTermsAccepted) {
          this.updatedWarning = 'We have updated our terms of service.'
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
    const currerntlyAcceptedTermsVersion = Number(
      this.userProfile.userTerms.termsOfUseAcceptedVersion.replace(/\D/g, '')
    )
    const latestVersionNumber = Number(latestVersionId.replace(/\D/g, ''))
    return (
      this.userProfile.userTerms.isTermsOfUseAccepted &&
      currerntlyAcceptedTermsVersion > latestVersionNumber
    )
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Terms and Conditions Container
$indent-width: 3rem;

.terms-container ::v-deep {
  article {
    padding: 2rem;
    // background: $gray1;
  }

  section {
    margin-top: 2rem;
  }

  section header {
    margin-bottom: 1rem;
    color: $gray9;
    text-transform: uppercase;
    letter-spacing: -0.02rem;
    font-size: 1.125rem;
    font-weight: 700;
  }

  section header > span {
    display: inline-block;
    width: $indent-width;
  }

  section div > p {
    padding-left: $indent-width;
  }

  section p:last-child {
    margin-bottom: 0;
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
