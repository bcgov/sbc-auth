<template>
  <v-container id="incorporate-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Incorporate or Register</h2>
        <v-list-item class="list-item">
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              If you have an approved Name Request (NR number), or you want a <NumberedCompanyTooltip />,
              you can start your Incorporation Application.
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <!-- Authenticated -->
        <template v-if="userProfile">
          <v-btn large color="#003366" class="mr-2 my-5 white--text"
            @click="emitManageBusinesses()">
            Incorporate a Named Company
          </v-btn>
          <v-btn large color="#003366" class="ml-2 my-5 white--text"
            @click="emitManageBusinesses(true)">
            Incorporate a Numbered Company
          </v-btn>
        </template>
        <!-- Not Authenticated -->
        <template v-else>
          <v-btn large color="#fcba19" @click="login()" class="mt-5">
            Log in with BC Services Card
          </v-btn>
          <p class="my-5">New to BC Registries? <a @click="emitAccountDialog()" class="create-account-link">
            <u>Create a BC Registries Account</u></a>
          </p>
        </template>
        <LearnMoreButton />
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Step3-Incorporate-x1.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import { Pages } from '@/util/constants'

@Component({
  components: {
    LearnMoreButton,
    NumberedCompanyTooltip
  }
})
export default class IncorpOrRegisterView extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'For Named Companies, add your existing Name Request number to your account and open it.' },
    { text: 'Establish your company\'s articles and prepare an Incorporation Agreement. Either create your own, or use template provided in the Incorporation Application.' },
    { text: 'Complete the Incorporation Application by providing information about your company: addresses, directors and share structure.' },
    { text: 'Retain a copy of all Incorporation documents for your business\'s records.' }
  ]

  @Prop() userProfile

  private login (): void {
    this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
  }

  @Emit('account-dialog')
  private emitAccountDialog () {}

  @Emit('manage-businesses')
  private emitManageBusinesses (isNumberedCompanyRequest: boolean = false) {
    return isNumberedCompanyRequest
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #incorporate-info-container {
    padding-top: 0!important;
    flex-wrap: wrap;

    a:hover {
      color: $BCgoveBueText2;
    }

    .list-item {
      align-items: flex-start;
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-bullet {
      color: $BCgovBullet;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 1rem;
      letter-spacing: 0;
      line-height: 1.5rem;
    }

    .v-btn {
      max-width: 300px;
      font-weight: bold;
    }
  }
</style>
