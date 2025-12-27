import React from 'react';
import { translate } from '@docusaurus/Translate';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme-original/Layout';
import RAGChatbot from '@site/src/components/RAGChatbot';

export default function LayoutWrapper(props) {
  const { siteConfig } = useDocusaurusContext();
  return (
    <>
      <Layout {...props}>
        {props.children}
        <RAGChatbot />
      </Layout>
    </>
  );
}