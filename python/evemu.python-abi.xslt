<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8" indent="yes" />
<xsl:strip-space elements="*"/>

<xsl:template match="function">
<xsl:text>    "</xsl:text><xsl:value-of select="name" /><xsl:text>": {
         "argtypes": (</xsl:text>
<xsl:for-each select="args/arg">
<xsl:choose>
    <xsl:when test="@type = 'int'" ><xsl:text>c_int, </xsl:text></xsl:when>
    <xsl:when test="@type = 'unsigned int'" ><xsl:text>c_uint, </xsl:text></xsl:when>
    <xsl:when test="contains(@type, 'char *')" ><xsl:text>c_char_p, </xsl:text></xsl:when>
    <xsl:otherwise><xsl:text>c_void_p,</xsl:text></xsl:otherwise>
</xsl:choose>
</xsl:for-each>
<xsl:text>),
         "restype": </xsl:text>
<xsl:choose>
    <xsl:when test="retval = 'int'" ><xsl:text>c_int</xsl:text></xsl:when>
    <xsl:when test="retval = 'unsigned int'" ><xsl:text>c_uint</xsl:text></xsl:when>
    <xsl:when test="contains(retval, 'char *')" ><xsl:text>c_char_p</xsl:text></xsl:when>
    <xsl:when test="retval = 'void'" ><xsl:text>None</xsl:text></xsl:when>
    <xsl:otherwise><xsl:text>c_void_p</xsl:text></xsl:otherwise>
</xsl:choose>
<xsl:text>
    },&#xa;</xsl:text>
</xsl:template>

<xsl:template match="header">
    <xsl:text>
# THIS FILE IS GENERATED FROM evemu.xml. DO NOT EDIT

# Import types directly, so they don't have to be prefixed with "ctypes.".
from ctypes import c_char_p, c_int, c_uint, c_void_p

api_prototypes = {
</xsl:text>
    <xsl:apply-templates select="function"/>
    <xsl:text>}</xsl:text>
    <xsl:text>&#xa;</xsl:text>
</xsl:template>
</xsl:stylesheet>
