package com.example.realestate.controller;

import com.example.realestate.model.CommunityPrice;
import com.example.realestate.service.PriceDataService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class PriceApiController {
    private final PriceDataService priceDataService;

    public PriceApiController(PriceDataService priceDataService) {
        this.priceDataService = priceDataService;
    }

    @GetMapping("/prices")
    public List<CommunityPrice> prices() {
        return priceDataService.getPrices();
    }
}
