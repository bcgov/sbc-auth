<template>
  <section>
    <h2 class="mb-5">{{`${tabNumber !==null ?  `${tabNumber}.` : ''} ${title}`}}</h2>
    <v-row>
        <v-col class="cols-12 col-sm-3 py-2">Notary Name</v-col>
        <v-col class="py-2">{{ accountNotaryName }}</v-col>
      </v-row>
      <v-row v-if="accountNotaryContact">
        <v-col class="cols-12 col-sm-3 py-2">Mailing Address</v-col>
        <v-col class="py-2">
          <div>
            <ul class="mailing-address">
              <li>{{ accountNotaryContact.street }}</li>
              <li>{{ accountNotaryContact.city }} {{ accountNotaryContact.region }} {{ accountNotaryContact.postalCode }}</li>
              <li>{{ accountNotaryContact.country }}</li>
            </ul>
          </div>
          </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">Email Address</v-col>
        <v-col class="py-2">{{ accountNotaryContact.email }}</v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">Phone Number</v-col>
        <v-col class="py-2">{{ accountNotaryContact.phone }}</v-col>
      </v-row>
  </section>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Contact } from '@/models/contact'

@Component({})
export default class NotaryInformation extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: 'Notary Information' }) private title: string
  @Prop({ default: {} }) accountNotaryContact: Contact
  @Prop({ default: '' }) accountNotaryName: string
}
</script>

<style lang="scss" scoped>
  // BC Online Account Information
  .bcol-acc__name {
    font-size: 1.125rem;
    font-weight: 700;
  }

  .bcol-acc__meta {
    margin: 0;
    padding: 0;
    list-style-type: none;
    font-size: .925rem;

    li {
      position: relative;
      display: inline-block
    }

    li + li {
      &:before {
        content: ' | ';
        display: inline-block;
        position: relative;
        top: -2px;
        left: 2px;
        width: 2rem;
        vertical-align: top;
        text-align: center;
      }
    }
  }

  .mailing-address {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }

  // .select-button {
  //   width: 8.75rem;
  // }

  // .crumbs a {
  //   font-size: 0.875rem;
  //   text-decoration: none;

  //   i {
  //     margin-top: -2px;
  //   }
  // }

  // .crumbs a:hover {
  //   span {
  //     text-decoration: underline;
  //   }
  // }
</style>
