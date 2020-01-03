import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Button } from 'reactstrap';
import { ListGroup, ListGroupItem } from 'reactstrap';

import Page from 'demo/page';

import { RouterApp, AppRoute, AppLink } from 'demo/approuter';

import styles from './index.scss';


export default function ChatApp({prefix}) {
    return <Page appTitle="Chat" appLink={prefix}>
        <Container className="py-3">
            <h2>Chat</h2>
            <RouterApp prefix={prefix}>
                <AppRoute exact path={["", "/:channelName"]}
                          render={({match: {params: {channelName}}}) =>
                              <ChatUI channelName={channelName} /> } />
            </RouterApp>
        </Container>
    </Page>;
}


class ChatUI extends React.Component {

    state = {
        userName: `User ${Math.floor(Math.random() * 10000)}`,
        message: '',
        channels: [
            'general', 'one', 'two', 'three',
        ],
    }

    render() {
        const {channelName} = this.props;

        const onUsernameChange = event => {
            this.setState({userName: event.target.value});
        };

        const onMessageChange = event => {
            this.setState({message: event.target.value});
        };

        const onSubmit = event => {
            event.preventDefault();
            const {userName, message} = this.state;
            const {channelName} = this.props;
            console.log('Submit message', {channelName, userName, message});
            this.setState({message: ''});
        };

        return <div className={styles.chat}>
            <div className={styles.sidebar}>
                {this.renderChannelsList()}
            </div>
            <div className={styles.main}>

                {this.renderChannelMessages(channelName)}

                <div className={styles.messageComposeLine}>
                    <form onSubmit={onSubmit} method="POST" action="#">
                        <div className={styles.composeRow}>
                            <input type="text"
                                   className={styles.fieldUsername}
                                   value={this.state.userName}
                                   onChange={onUsernameChange} />
                            <input type="text"
                                   className={styles.fieldMessage}
                                   value={this.state.message}
                                   onChange={onMessageChange} />
                            <button className={styles.sendButton}
                                    type="submit">SEND</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>;
    }

    renderChannelsList() {
        const {channels} = this.state;
        const {channelName} = this.props;

        return <ListGroup flush>
            {channels.map(name =>
                <ListGroupItem key={name}
                               tag={AppLink}
                               to={`/${name}`}
                               action
                               active={name === channelName}>
                    #{name}
                </ListGroupItem>)}
        </ListGroup>;
    }

    renderChannelMessages(channelName) {

        if (!channelName) {
            return <div className={styles.noChannelMessage}>
                <div>Select a channel</div>
            </div>;
        }

        return <div className={styles.messagesContainer}>
            Messages for #{channelName}
        </div>;
    }

}


function ChatUI2({channelName}) {

    const activeChannels = [
        'general', 'one', 'two', 'three',
    ];

    return <div>
        <div>
            <h3>Channels</h3>
            <ul>
                {activeChannels.map(name =>
                    <li key={name}>
                        <AppLink to={`/${name}`}>
                            #{name}
                        </AppLink>
                    </li>)}
            </ul>
        </div>
        <div>
            <ChannelUI channelName={channelName} />
        </div>
    </div>;
}


function ChannelUI({channelName}) {
    if (!channelName) {
        return <div>No channel selected</div>;
    }
    return <div>
        <h3>Channel: #{channelName}</h3>
        Messages here...
    </div>;
}
