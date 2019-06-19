import React from 'react';
import graphql from 'graphql-tag';
import { Subscription } from 'react-apollo';


const STATUS_UPDATES_SUBSCRIPTION = graphql`
    subscription {
        currentTime
    }
`;


export default function CurrentTime() {
    return <Subscription subscription={STATUS_UPDATES_SUBSCRIPTION}>
        {({data}) => data ? data.currentTime : '- - -'}
    </Subscription>;
}
