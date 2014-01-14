<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8" indent="yes" />
<xsl:strip-space elements="*"/>

<xsl:template match="function">
/**
<xsl:value-of select="doc" />
*/
<xsl:value-of select="retval" /><xsl:text> </xsl:text>
<xsl:value-of select="name" /><xsl:text>(</xsl:text>
<xsl:for-each select="args/arg">
    <xsl:value-of select="@type"/><xsl:text> </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:if test="following-sibling::*">,</xsl:if>
</xsl:for-each>);
</xsl:template>

<xsl:template match="header">
    <xsl:value-of select="copyright"/>
    <xsl:text>&#xa;</xsl:text>
    <xsl:text>

/** THIS FILE IS GENERATED FROM evemu.xml. DO NOT EDIT */

#ifndef EVEMU_H
#define EVEMU_H

#include &lt;stdio.h&gt;
#include &lt;errno.h&gt;
#include &lt;linux/input.h&gt;

#ifdef __cplusplus
extern "C" {
#endif
    </xsl:text>
    <xsl:text>&#xa;</xsl:text>
    <xsl:text>#define EVEMU_VERSION </xsl:text><xsl:value-of select="version/@version"/>
    <xsl:text>&#xa;</xsl:text>
    <xsl:apply-templates select="function"/>
    <xsl:text>
#ifdef __cplusplus
}
#endif

#endif
    </xsl:text>
    <xsl:text>&#xa;</xsl:text>
</xsl:template>
</xsl:stylesheet>
