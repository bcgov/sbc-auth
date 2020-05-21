<template>
  <v-container id="incorporate-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Incorporate or Register</h2>
        <v-list-item class="list-item">
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              If you have an approved Name Request (NR number), or you want a <NumberedCompanyTooltip />,
              you can start your Incorporation Application.
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <!-- Authenticated -->
        <div v-if="userProfile">
          <v-btn large color="#003366" class="mr-2 mb-5 white--text"
            @click="emitManageBusinesses()">
            Incorporate a Named Company
          </v-btn>
          <v-btn large color="#003366" class="ml-2 mb-5 white--text"
            @click="emitManageBusinesses(true)">
            Incorporate a Numbered Company
          </v-btn>
        </div>
        <!-- Not Authenticated -->
        <div v-else class="incorporate-info-btns">
          <v-btn large color="#fcba19" @click="login()" class="mt-5">
            Log in with BC Services Card
          </v-btn>
          <p class="my-5">New to BC Registries? <a @click="emitAccountDialog()" class="create-account-link">
            <u>Create a BC Registries Account</u></a>
          </p>
        </div>
        <v-btn large outlined color="#003366" class="btn-learn-more"
          href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
          target="_blank" rel="noopener noreferrer">
          Learn More
        </v-btn>
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
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import { Pages } from '@/util/constants'

@Component({
  components: {
    NumberedCompanyTooltip
  }
})
export default class IncorpOrRegisterInfo extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'For Name Companies, add your existing Name Request number to your account and open it.' },
    { text: 'Establish your company\'s articles and prepare an incorporation agreement. Either create your own, or use template provided in the incorporation application.' },
    { text: 'Complete the Incorporation application by providing information about your company: addresses, directors and share structure.' },
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
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-bullet {
      color: #CCCCCC;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 16px;
      letter-spacing: 0;
      line-height: 24px;
    }

    .v-btn {
      max-width: 300px;
      font-weight: bold;
    }

    .incorporate-info-btns {
      display: flex;
      flex-direction: column;
    }

    .btn-learn-more {
      font-weight: bold;
      width: 160px;
    }
  }
</style>
