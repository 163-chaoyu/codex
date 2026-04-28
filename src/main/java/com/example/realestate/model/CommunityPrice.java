package com.example.realestate.model;

public class CommunityPrice {
    private String communityName;
    private String district;
    private int avgUnitPrice;
    private String source;
    private String crawlDate;

    public String getCommunityName() {
        return communityName;
    }

    public void setCommunityName(String communityName) {
        this.communityName = communityName;
    }

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public int getAvgUnitPrice() {
        return avgUnitPrice;
    }

    public void setAvgUnitPrice(int avgUnitPrice) {
        this.avgUnitPrice = avgUnitPrice;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getCrawlDate() {
        return crawlDate;
    }

    public void setCrawlDate(String crawlDate) {
        this.crawlDate = crawlDate;
    }
}
