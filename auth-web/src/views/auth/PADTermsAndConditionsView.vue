<template>
  <v-container class="terms-of-use-container view-container">
    <h1 class="mb-10">Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services</h1>
    <v-card flat>
      <v-card-text class="pa-8">
        <TermsOfUse
          :tosType="'termsofuse_pad'"
        ></TermsOfUse>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { LoginSource, Pages } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import Vue from 'vue'

@Component({
  components: {
    TermsOfUse
  }
})

export default class PADTermsAndConditionsView extends Vue {
}

</script>

<style lang="scss" scoped>
  .terms-of-use-container {
    max-width: 65rem;
  }

  // TODO: Payor Authoriztion section of the PAD Terms does not apply in this content so we don't display it
  // TODO: Better strategy to show/hide this content VS hacking it out with styling
  ::v-deep section:last-child {
    display: none;
  }

  // Terms and Conditions Container
  $indent-width: 1rem;

  .terms-container {
    p, li {
      margin: 1rem 0;
    }

    ol {
      margin-left: $indent-width;
    }

    li {
      padding-left: $indent-width;
    }

    h3 {
      max-width: 55ch;
    }

    section {
      margin-bottom: 2rem;
    }

    section:last-child {
      margin-bottom: 0;
    }

    section header {
      margin-bottom: 1rem;
      font-size: 1rem;
      font-weight: 700 !important;
    }

    section header > span {
      display: inline-block;
      width: $indent-width;
    }

    section a {
      font-weight: 600;
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
