<template>
  <section class="help-content">
    <header class="d-flex justify-center mt-2">
      <p class="mt-2">
        <strong class="font-weight-bold header">{{ helpContent.header }}</strong>
      </p>
    </header>
    <div class="help-text mt-4">
      <p class="mb-n3">
        {{ helpContent.intro }}
      </p>
      <ol class="bold">
        <li
          v-for="(step, index1) in helpContent.steps"
          :key="'step' + index1"
          class="mt-10"
        >
          <span class="font-weight-black header">{{ step.title }}</span>
          <ul
            v-for="(itemList, index2) in step.itemList"
            :key="'itemList' + index2"
            class="mt-4 ml-2 bullet-none"
          >
            <span
              v-if="itemList.itemTitle"
              class="ml-n8"
            >
              <strong class="font-weight-bold">{{ itemList.itemTitle }}</strong>
            </span>
            <v-spacer class="mb-4" />
            <li
              v-for="(item, index3) in itemList.items"
              :key="'item' + index3"
            >
              <v-row>
                <v-col
                  cols="1"
                  class="pt-1 pb-1 ml-n12"
                >
                  <v-icon>mdi-circle-small</v-icon>
                </v-col>
                <v-col
                  cols="11"
                  class="pt-1 pb-1 ml-n12"
                >
                  <p v-if="typeof item === 'string'">
                    {{ item }}
                  </p>
                  <p
                    v-else
                    v-html="item.content"
                  />
                </v-col>
              </v-row>
            </li>
            <ul
              v-for="(subItem, index4) in itemList.subItems"
              :key="'subItem' + index4"
              class="mb-2"
            >
              <li>
                <v-row>
                  <v-col
                    cols="1"
                    class="pt-1 mb-n6 ml-n12"
                  >
                    <v-icon>mdi-circle-small</v-icon>
                  </v-col>
                  <v-col
                    cols="11"
                    class="pt-1 mb-n6 ml-n12"
                  >
                    {{ subItem }}
                  </v-col>
                </v-row>
              </li>
            </ul>
          </ul>
        </li>
      </ol>
    </div>
  </section>
</template>

<script lang="ts">
export default {
  data () {
    return {
      helpContent: {
        header: 'Help with Starting and Managing a Business',
        intro: 'Start a named or numbered business in B.C. by following these steps:',
        steps: [
          {
            title: `Decide on a Business Type`,
            itemList: [
              {
                items: [
                  {
                    content: `Decide which business structure is the most appropriate for you. A few options are: a sole 
                          proprietorship, partnership, or corporation. Each structure has different legal and financial 
                          implications. <a href='https://entity-selection-prod.apps.silver.devops.gov.bc.ca/'>
                          Use the Business Structures Wizard to help you decide.</a>`,
                    isHtml: true
                  },
                  `If you want to start a corporation, you also have the choice of using a named or numbered company.`,
                  `Once your Name Request has been approved you must return to this screen to Incorporate or Register 
                     your business using your approved Name Request.`
                ]
              }
            ]
          },
          {
            title: `Request a Business Name or Use a Numbered Company`,
            itemList: [
              {
                itemTitle: `Request a Business Name`,
                items: [
                  {
                    content: `To start a named business in B.C., change the business name of an existing company, or 
                          merge two or more companies using a new name, click the
                          <strong>"Get Started with a B.C. Based Business"</strong> button on this
                          screen and follow the instructions.`,
                    isHtml: true
                  },
                  `Before registering or incorporating a named business, you will need to first submit a Name Request. 
                    You will be asked to create a unique name for your business and submit your name(s) for review by BC 
                    Registries staff.`,
                  `Once you submit your Name Request you can return to this screen and your Name Request (NR) will 
                    automatically appear in your table.`,
                  `If you do not see your Name Request in your table (e.g. if you submitted your Name Request without 
                    being logged into your BC Registries account), you can add your Name Request manually by looking up 
                    your business name or your NR number.`,
                  {
                    content: `You can track the approval status of your Name Request from your table on this screen by 
                      clicking the <strong>"Open Name Request"</strong> button next to your Name Request.`,
                    isHtml: true
                  }
                ]
              },
              {
                itemTitle: `Use a Numbered Company`,
                items: [
                  {
                    content: `To start a numbered corporation in B.C., click the <strong>"Get Started with a B.C. Based 
                      Business"</strong> button and follow the instructions.`,
                    isHtml: true
                  }

                ]
              }
            ]
          },
          {
            title: `Incorporate or Register Your Business`,
            itemList: [
              {
                items: [
                  {
                    content: `For named businesses, once your Name Request has been approved and added to your table on 
                      this screen, you must select the <strong>"Register Now"</strong> button beside the name to begin 
                      your incorporation or registration.`,
                    isHtml: true
                  },
                  `Follow the steps in the application and complete all of the required information including addresses, 
                     contact information, people and roles, and share structure (if applicable).`,
                  `Retain a copy of all incorporation or registration documents for your business' records.`
                ]
              }
            ]
          },
          {
            title: `Manage and Maintain Your Business`,
            itemList: [
              {
                items: [
                  `Once your business is incorporated or registered you are required to keep information about your 
                     business up to date with the Business Registry.`,
                  {
                    content: `From your table, click <strong>"Manage Business"</strong> to manage and maintain your 
                      business information including:`,
                    isHtml: true
                  }
                ],
                subItems: [
                  'View and change business information.',
                  'See when annual reports are due and file them each year (if applicable).',
                  "See the history of your business' filings and download copies of all documents.",
                  'Dissolve your business.'
                ]
              }
            ]
          }
        ]
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.title-text {
    color: $app-blue;
}

.help-text {
    width: 80%;
    margin: 0 auto;
}

ol.bold li::marker {
    font-weight: bold;
    font-size: $px-20 !important;
}

ul.bullet-none li::marker  {
    content: none
}

.header {
    font-size: $px-20 !important;
}

</style>
