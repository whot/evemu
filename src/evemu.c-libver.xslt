<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8" indent="yes" />
<xsl:strip-space elements="*"/>

<xsl:template match="header">
<xsl:text>EVEMU_2.0 {
  global:
</xsl:text>
<xsl:for-each select="function">
	<xsl:sort select="name" data-type="text" order="ascending" />
	<xsl:text>    </xsl:text><xsl:value-of select="name" /><xsl:text>;&#xa;</xsl:text>
	</xsl:for-each>
	<xsl:text>
  local:
    *;
};
</xsl:text>
</xsl:template>
</xsl:stylesheet>
