package com.example.realestate.service;

import com.example.realestate.model.CommunityPrice;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

@Service
public class PriceDataService {
    private final ObjectMapper objectMapper;

    public PriceDataService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public List<CommunityPrice> getPrices() {
        ClassPathResource resource = new ClassPathResource("data/nanjing_prices.json");
        try (InputStream inputStream = resource.getInputStream()) {
            List<CommunityPrice> prices = objectMapper.readValue(inputStream, new TypeReference<>() {});
            prices.sort(Comparator.comparingInt(CommunityPrice::getAvgUnitPrice).reversed());
            return prices;
        } catch (IOException ex) {
            return Collections.emptyList();
        }
    }
}
