<template>
  <v-container id="maintain-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Manage and Maintain Your Business</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
            <v-list-item class="list-item list-item-sub" v-for="(item, index) in item.subText" :key="`sub-${index}`">
              <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
              <v-list-item-content>
                <v-list-item-subtitle class="list-item-text">
                  {{item.text}}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
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
          <LearnMoreButton />
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
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'

@Component({
  components: {
    LearnMoreButton
  }
})
export default class MaintainBusinessView extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'Once your business is incorporated or registered you are required to keep information about your business up to date with the Registry.' },
    { text: 'By managing your business through your BC Registry account you can:',
      subText: [
        { text: 'See which Annual Reports are due and file each year.' },
        { text: 'View and change your current directors and addresses by filing Director and Address Changes.' },
        { text: 'See the history of your business\' filings and download copies of all documents including your Certificate of Incorporation and more.' }
      ]
    }
  ]

  @Prop()
  private userProfile: User

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
      align-items: flex-start;
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-sub {
      padding-left: 1.5rem;
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

    .maintain-info-btns {
      display: flex;
      flex-direction: column;

      .v-btn {
        max-width: 250px;
        font-weight: bold;
      }
    }
  }
</style>
