<template>
  <v-container id="maintain-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Manage and Maintain Your Business</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Sub Bullet Points -->
        <v-list-item class="list-item list-item-sub" v-for="(item, index) in subBulletPoints" :key="`Sub-index: ${index}`">
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <div class="maintain-info-btns">
          <v-btn v-if="userProfile" large color="#fcba19" class="my-5"
            @click="emitManageBusinesses()">
            Manage an Existing Business
          </v-btn>
          <v-btn v-else large color="#fcba19" @click="login()" class="my-5">
            Log in with BC Services Card
          </v-btn>
          <v-btn large outlined color="#003366" class="btn-learn-more"
            href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
            target="_blank" rel="noopener noreferrer">
            Learn More
          </v-btn>
        </div>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Step4-Maintain-x1.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Pages } from '@/util/constants'

@Component({})
export default class MaintainBusinessInfo extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'Once your business is incorporated or registered you are required to keep information about your business up to date with the Registry.' },
    { text: 'By managing your business throught your BC registry account you can:' }
  ]

  private subBulletPoints: Array<any> = [
    { text: 'See which Annual Reports are due and file each year.' },
    { text: 'View and change your current directors and addresses by filing Director and Address Changes.' },
    { text: 'See the history of your business\' filings and download copies of all documents including your Certificate of Incorporation and more.' }
  ]

  @Prop() userProfile

  private login (): void {
    this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
  }

  @Emit('manage-businesses')
  private emitManageBusinesses () {}
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #maintain-info-container {
    padding-top: 0!important;
    flex-wrap: wrap;

    .list-item {
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-sub {
      padding-left: 2.5rem;
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

    .maintain-info-btns {
      display: flex;
      flex-direction: column;

      .v-btn {
        max-width: 250px;
        font-weight: bold;
      }

      .btn-learn-more {
        font-weight: bold;
        width: 160px;
      }
    }
  }
</style>
