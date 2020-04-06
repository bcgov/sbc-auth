<template>
  <div>
    <v-fade-transition>
      <div class="loading-container" v-if="!termsContent">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="termsContent"/>
      </div>
    </v-fade-transition>
    <div v-html="termsContent" class="terms-container"></div>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import documentService from '@/services/document.services.ts'

@Component({
  computed: {
    ...mapState('user', ['termsOfUse'])
  },
  methods: {
    ...mapMutations('user', ['setTermsOfUse'])
  }
})

export default class TermsOfUse extends Vue {
  private readonly setTermsOfUse!: (terms: TermsOfUseDocument) => void
  private termsContent = ''

  @Prop({ default: '' }) private content: string

  async mounted () {
    if (!this.content) {
      const response = await documentService.getTermsOfService('termsofuse')
      if (response.data) {
        this.termsContent = response.data.content
        this.setTermsOfUse(response.data)
      }
    } else {
      this.termsContent = this.content
    }
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
