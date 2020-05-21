<template>
  <v-container id="request-name-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Request a Name or Use a Numbered Company</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index" >
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <div class="request-name-info-btns mt-5">
          <v-btn large color="#003366" class="white--text"
            href="https://www.bcregistrynames.gov.bc.ca/nro/" target="_blank" rel="noopener noreferrer">
            Request a Name
          </v-btn>
          <p class="my-5">Have an existing Name Request?
            <a href="https://www.bcregistrynames.gov.bc.ca/nro/nro.htm?_flowId=anonymous-monitor-flow&_flowExecutionKey=e1s1"
              target="_blank" rel="noopener noreferrer">
              Check your Name Request Status
            </a>
          </p>
          <v-btn large outlined color="#003366"
            href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
            target="_blank" rel="noopener noreferrer">
            Learn More
          </v-btn>
        </div>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Step2-Name-Request.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class RequestNameInfo extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'Create a unique name that ensures the public is not confused or misled by similar corporate names.' },
    { text: 'Submit this name for examination by the Business Registry' },
    { text: 'If your name is approved, you can use it to incorporate or register your business.' },
    { text: `You can choose to incorporate a numbered Benefit Company and start your incorporation immediately.` }
  ]
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #request-name-info-container {
    padding-top: 0!important;
    flex-wrap: wrap;

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

    .request-name-info-btns {
      display: flex;
      flex-direction: column;

      .v-btn {
        font-weight: bold;
        width: 160px;
      }
    }
  }
</style>
