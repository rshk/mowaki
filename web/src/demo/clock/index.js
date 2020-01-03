import React from 'react';
import graphql from 'graphql-tag';
import { Subscription } from 'react-apollo';
import { Container } from 'reactstrap';

import Page from 'demo/page';


const STATUS_UPDATES_SUBSCRIPTION = graphql`
    subscription {
        currentTime
    }
`;


export default function ClockDemo({prefix}) {
    return <Page appTitle="Clock" appLink={prefix}>
        <Container className="py-3">
            <div className="text-center">
                <h2>Current server time</h2>
                <div className="my-5" style={{fontSize: '80px'}}>
                    <CurrentTime />
                </div>
                <div className="text-muted">
                    Server time (UTC), updated via websocket / GraphQL subscription.
                </div>
            </div>
        </Container>
    </Page>;
}


function CurrentTime() {
    return <Subscription subscription={STATUS_UPDATES_SUBSCRIPTION}>
        {({data}) => data ? data.currentTime : null}
    </Subscription>;
}
